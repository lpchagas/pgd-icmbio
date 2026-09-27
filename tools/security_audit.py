"""Auditoria de segredos sem revelar os valores pesquisados.

Dois modos:

* legado (sem ``--alvos``): procura, nos arquivos locais, os valores exatos das
  credenciais do ``.env``. É o modo usado no CI.
* auditoria completa (``--alvos``): ``detect-secrets`` mais as regras do projeto
  (valor exato, CPF válido, dump por conteúdo, links e arquivos proibidos) sobre
  quatro alvos: ``arquivos`` (disco), ``indice`` (blobs do índice, não o disco),
  ``historico`` (blobs, links, mensagens e tags das refs informadas) e
  ``proibidos`` (caminhos dos três anteriores).

O valor sensível é lido do ``.env`` apenas em memória, e o conteúdo varrido é
entregue ao detector também em memória: nada é gravado em disco. O relatório
contém somente caminhos, linhas, regras, códigos de erro e quantidades; nunca o
segredo, seu hash, trechos vizinhos ou mensagens brutas de erro. A auditoria
completa termina em ``completo_sem_ocorrencia``, ``completo_com_ocorrencia`` ou
``incompleto``; ``incompleto`` nunca é sucesso. Nenhum modo de auditoria altera
arquivos; só ``--remediate`` (legado) o faz.

Ocorrências conhecidas (L4e): o histórico foi mantido (H9) e guarda falsos positivos
e fixtures sintéticas já revisados. Eles ficam em
``config/auditoria-ocorrencias-conhecidas.json``, com justificativa, e são separados
em ``ocorrencias_conhecidas``; o status só considera as ocorrências **não revisadas**.
Valor exato, CPF válido e dump por conteúdo nunca podem ser declarados conhecidos.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import logging
import os
import platform
import posixpath
import re
import stat
import subprocess
import sys
from collections import deque
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KEYS = ("DENODO_USER", "DENODO_PASSWORD", "DENODO_PASS", "MYSQL_PASSWORD", "ANTHROPIC_API_KEY")
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "node_modules", "artefatos_local", "cgov", "setup"}
TEXT_SUFFIXES = {
    "", ".md", ".txt", ".py", ".json", ".toml", ".yaml", ".yml", ".ini",
    ".cfg", ".env", ".sql", ".csv", ".ipynb", ".ps1", ".sh",
}

# ─── Auditoria completa ──────────────────────────────────────────────────────
RULES_VERSION = "2026.09.27-l4e"
KNOWN_FILE = ROOT / "config" / "auditoria-ocorrencias-conhecidas.json"
# Regras que indicam dado real: nunca aceitas na lista de conhecidas.
NEVER_KNOWN = ("valor_exato", "cpf_valido", "dump_sql_por_conteudo")
DETECT_SECRETS_VERSION = "1.5.0"
ALL_TARGETS = ("arquivos", "indice", "historico", "proibidos")
MAX_BYTES = 20 * 1024 * 1024
MIN_EXACT_LENGTH = 4
MAX_LINK_HOPS = 40
STATUS_EXIT = {"completo_sem_ocorrencia": 0, "completo_com_ocorrencia": 1, "incompleto": 2}

# Filtros do detect-secrets que decidem só pelo nome do arquivo. Ficam desativados:
# a auditoria varre todo conteúdo textual e registra as próprias exclusões.
DISABLED_FILTERS = (
    "detect_secrets.filters.common.is_invalid_file",
    "detect_secrets.filters.heuristic.is_lock_file",
    "detect_secrets.filters.heuristic.is_non_text_file",
    "detect_secrets.filters.heuristic.is_swagger_file",
)

PLACEHOLDERS = frozenset({
    "sua_senha_aqui", "seu_cpf_aqui", "defina-a-senha", "defina-a-senha-local",
    "cole-a-chave-aqui", "cpf-do-usuario", "changeme", "example", "placeholder",
})
PLACEHOLDER_PATTERN = re.compile(
    r"^(<[^>]*>|\$\{[^}]*\}|\{\{.*\}\}|x{3,}|\*{3,}|(seu|sua)_[a-z_]+|defina-[a-z-]+|cole-[a-z-]+|[a-z_]+_aqui)$",
    re.IGNORECASE,
)
# Fonte única da política de caminhos privados: o teste documental e o
# tools/verificar_links.py consultam forbidden_reason com PRIVACY_REASONS.
# Instruções (H1, L4d): versionadas só como arquivos regulares da raiz comum; aninhadas
# (inclusive na raiz de agente/), como pasta ou por link continuam recusadas.
INSTRUCTIONS = {"agents.md", "claude.md", "project.md"}
PRIVATE_ANY_DEPTH = {".agents", ".claude", ".codex", "artefatos_local"}
# Privados na raiz de cada componente do repositório (ver PERFIS).
PRIVATE_COMPONENT_DIRS = {"cgov", "setup", "data", "testes_cgov"}
PERFIS = {
    # Layout atual: cada repositório auditado isoladamente; exceção SQL do agente em src/dados.
    "pre-merge": {
        "raizes": ("",),
        "sql_permitido": re.compile(r"^src/dados/(schema\.sql|migracoes/[0-9]{3}_[^/]+\.sql)$"),
    },
    # Monorepo (obrigatório a partir do L3): raiz comum e componente agente/.
    "monorepo": {
        "raizes": ("", "agente/"),
        "sql_permitido": re.compile(r"^agente/dados/(schema\.sql|migracoes/[0-9]{3}_[^/]+\.sql)$"),
    },
}
DEFAULT_PERFIL = "pre-merge"
# Motivos de forbidden_reason que significam conteúdo privado (não só não versionável).
PRIVACY_REASONS = frozenset({
    "area_privada", "instrucao_aninhada", "credencial_env", "credencial_cnf", "acervo_referencias_privado",
})


def is_private_path(path: str, perfil: str = DEFAULT_PERFIL) -> bool:
    """Caminho relativo à raiz do repositório aponta para área privada (política única)."""

    return forbidden_reason(path, perfil) in PRIVACY_REASONS
DUMP_NAME = re.compile(r"(\.dump\.sql|^pgd_agente_.*\.sql)$", re.IGNORECASE)
DUMP_CONTENT = re.compile(r"^(-- (MySQL|MariaDB) dump|-- Dump completed|/\*!40\d{3} SET )", re.MULTILINE)
ALLOWED_NOTEBOOKS = {"consultas_denodo_template.ipynb"}
CPF_PATTERN = re.compile(r"(?<![0-9A-Za-z])([0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}|[0-9]{11})(?![0-9A-Za-z])")
ALLOWLIST_PRAGMA = re.compile(r"pragma:\s*allowlist(\s+nextline)?\s+secret")
ENV_ASSIGNMENT = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_.]*)\s*=\s*(.*)$")
SYMLINK_MODE = "120000"
SUBMODULE_MODE = "160000"
CONTENT_CLASS = "conteudo_sensivel"
PATH_CLASS = "politica_caminho"
CONTENT_POLICY_CLASS = "politica_conteudo"


def _dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values


def _files(root: Path):
    """Percorre arquivos locais sem seguir junctions/symlinks privados."""

    for directory, names, filenames in os.walk(root, topdown=True, followlinks=False):
        names[:] = [name for name in names if name not in SKIP_DIRS and not (Path(directory) / name).is_symlink()]
        for filename in filenames:
            path = Path(directory) / filename
            if path.is_symlink() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                if path.stat().st_size <= 20 * 1024 * 1024:
                    yield path
            except OSError:
                continue


def scan_exact_secrets(
    root: Path = ROOT,
    env_path: Path | None = None,
    keys: tuple[str, ...] = DEFAULT_KEYS,
) -> dict:
    env_file = env_path or root / ".env"
    values = _dotenv(env_file)
    secrets = {key: values.get(key, "") for key in keys if values.get(key)}
    occurrences: list[dict[str, object]] = []
    for path in _files(root):
        if path.resolve() == env_file.resolve():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        matched = [key for key, secret in secrets.items() if secret and secret in text]
        if matched:
            occurrences.append({
                "arquivo": str(path.relative_to(root)),
                "variaveis": matched,
                "quantidade": sum(text.count(secrets[key]) for key in matched),
            })
    return {
        "tipo": "auditoria_segredo_exato",
        "credenciais_carregadas": sorted(secrets),
        "armazenamento_autorizado": str(env_file.relative_to(root)) if env_file.is_relative_to(root) else ".env externo",
        "ocorrencias_fora_do_armazenamento": occurrences,
        "status": "falha" if occurrences else "sucesso",
    }


def remediate_exact_secrets(
    root: Path = ROOT,
    env_path: Path | None = None,
    keys: tuple[str, ...] = DEFAULT_KEYS,
) -> dict:
    """Substitui somente ocorrências exatas fora do .env, sem copiar o segredo."""

    env_file = env_path or root / ".env"
    values = _dotenv(env_file)
    secrets = [values[key] for key in keys if values.get(key)]
    before = scan_exact_secrets(root, env_file, keys)
    changed: list[str] = []
    for occurrence in before["ocorrencias_fora_do_armazenamento"]:
        path = root / str(occurrence["arquivo"])
        content = path.read_text(encoding="utf-8", errors="replace")
        sanitized = content
        for secret in secrets:
            sanitized = sanitized.replace(secret, "<REMOVIDO: usar .env local>")
        if sanitized != content:
            path.write_text(sanitized, encoding="utf-8")
            changed.append(str(occurrence["arquivo"]))
    after = scan_exact_secrets(root, env_file, keys)
    after["arquivos_sanitizados"] = changed
    return after


# ─── Erros seguros ───────────────────────────────────────────────────────────


class AuditError(Exception):
    """Erro com código seguro: nunca carrega stderr, argumentos ou conteúdo."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _safe_error(exc: BaseException) -> str:
    return exc.code if isinstance(exc, AuditError) else type(exc).__name__


# ─── Regras do projeto ───────────────────────────────────────────────────────


def is_placeholder(value: str) -> bool:
    candidate = value.strip().strip('"\'')
    return candidate.lower() in PLACEHOLDERS or bool(PLACEHOLDER_PATTERN.match(candidate))


def cpf_is_valid(raw: str) -> bool:
    digits = [int(char) for char in raw if char.isdigit()]
    if len(digits) != 11 or len(set(digits)) == 1:
        return False
    for size in (9, 10):
        total = sum(digit * weight for digit, weight in zip(digits[:size], range(size + 1, 1, -1)))
        check = (total * 10) % 11 % 10
        if check != digits[size]:
            return False
    return True


def _perfil(perfil: str) -> dict:
    if perfil not in PERFIS:
        raise ValueError(f"perfil desconhecido: {perfil}")
    return PERFIS[perfil]


def forbidden_reason(path: str, perfil: str = DEFAULT_PERFIL) -> str | None:
    """Motivo pelo qual o caminho não pode ser versionado no perfil, ou ``None``."""

    config = _perfil(perfil)
    posix = PurePosixPath(path.replace("\\", "/"))
    lower = str(posix).lower()
    parts = [part.lower() for part in posix.parts]
    name = posix.name.lower()
    suffix = posix.suffix.lower()
    if set(parts) & PRIVATE_ANY_DEPTH:
        return "area_privada"
    for raiz in config["raizes"]:
        # RL1v2-06: as mesmas regras de raiz valem para cada componente do perfil.
        resto = lower[len(raiz):] if lower.startswith(raiz) else None
        if resto is not None and (resto.split("/", 1)[0] in PRIVATE_COMPONENT_DIRS or resto.startswith(".github/skills/")):
            return "area_privada"
    # RL1v2-06 e L4d: nome de instrução só é versionável como arquivo da raiz comum.
    if set(parts) & INSTRUCTIONS and not (len(parts) == 1 and name in INSTRUCTIONS):
        return "instrucao_aninhada"
    if name.startswith(".env") and name != ".env.example":
        return "credencial_env"
    if suffix == ".cnf":
        return "credencial_cnf"
    for raiz in config["raizes"]:
        acervo = f"{raiz}docs/referencias-pgd/"
        if lower.startswith(acervo) and lower != f"{acervo}readme.md":
            return "acervo_referencias_privado"
    if suffix == ".dump" or ".sql." in name or DUMP_NAME.search(name):
        return "dump_sql"
    if suffix == ".sql" and not config["sql_permitido"].match(str(posix)):
        return "sql_fora_da_excecao"
    if suffix in {".csv", ".xls", ".xlsx"} and not lower.startswith("tests/fixtures/"):
        return "planilha_fora_de_fixture"
    if suffix in {".pdf", ".ppt", ".pptx", ".doc", ".docx"}:
        return "documento_nao_versionavel"
    if suffix == ".ipynb" and name not in ALLOWED_NOTEBOOKS:
        return "notebook_com_resultado"
    return None


def _lexical_target(link_path: str, target: str) -> tuple[str | None, str | None]:
    """(caminho resolvido lexicalmente, motivo de recusa) de um salto de link."""

    target = target.strip().replace("\\", "/")
    if target.startswith("/") or re.match(r"^[A-Za-z]:", target):
        return None, "symlink_absoluto"
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(link_path.replace("\\", "/")), target))
    if resolved == ".." or resolved.startswith("../"):
        return None, "symlink_fora_da_raiz"
    return resolved, None


def symlink_reason(link_path: str, target: str, perfil: str = DEFAULT_PERFIL) -> str | None:
    """Motivo de recusa de um salto de link: absoluto, fora da raiz ou para caminho proibido."""

    if _is_instruction(link_path):
        return "instrucao_como_link"
    resolved, reason = _lexical_target(link_path, target)
    if reason:
        return reason
    forbidden = forbidden_reason(resolved, perfil)
    if forbidden:
        return f"symlink_para_caminho_proibido:{forbidden}"
    return "symlink_para_instrucao" if _is_instruction(resolved) else None


def _is_instruction(path: str) -> bool:
    """Arquivo de instrução pelo nome: ele próprio não pode ser link nem alvo de link."""

    return PurePosixPath(path.replace("\\", "/")).name.lower() in INSTRUCTIONS


def link_chain_reason(link_path: str, lookup, perfil: str = DEFAULT_PERFIL) -> str | None:
    """Resolve uma cadeia de links só com ``lookup(caminho) -> alvo | None``.

    ``lookup`` consulta o mapa de links da mesma origem (índice, árvore do commit ou
    metadados do disco); o conteúdo apontado nunca é lido. Cada salto passa por
    ``symlink_reason``, e componentes intermediários que sejam links também são
    seguidos. Ciclos e cadeias longas demais são recusados.
    """

    if lookup(link_path) is None:
        return None
    if _is_instruction(link_path):
        return "instrucao_como_link"
    pending = deque(link_path.replace("\\", "/").split("/"))
    resolved: list[str] = []
    hops = 0
    while pending:
        component = pending.popleft()
        if component in ("", "."):
            continue
        if component == "..":
            if not resolved:
                return "symlink_fora_da_raiz"
            resolved.pop()
            continue
        candidate = "/".join([*resolved, component])
        target = lookup(candidate)
        if target is None:
            resolved.append(component)
            if hops:
                forbidden = forbidden_reason(candidate, perfil)
                if forbidden:
                    return f"symlink_para_caminho_proibido:{forbidden}"
                if _is_instruction(candidate):
                    return "symlink_para_instrucao"
            continue
        hops += 1
        if hops > MAX_LINK_HOPS:
            return "symlink_ciclo"
        target = target.strip().replace("\\", "/")
        if target.startswith("/") or re.match(r"^[A-Za-z]:", target):
            return "symlink_absoluto"
        pending.extendleft(reversed(target.split("/")))
    return None


def _project_rules(text: str, exact: dict[str, str]) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    for key, value in exact.items():
        start = text.find(value)
        while start != -1:
            findings.append((_line_of(text, start), f"valor_exato:{key}"))
            start = text.find(value, start + len(value))
    for match in CPF_PATTERN.finditer(text):
        if cpf_is_valid(match.group(1)):
            findings.append((_line_of(text, match.start()), "cpf_valido"))
    return findings


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


# ─── .env do modo exato (gramática estrita) ──────────────────────────────────


def _parse_env(text: str) -> tuple[dict[str, str], list[tuple[int, str | None]]]:
    """Interpreta um .env com gramática estrita; devolve valores e problemas por linha.

    Aceita: comentários, linhas vazias, ``export`` opcional, valor sem aspas (até
    `` #``), entre aspas simples ou duplas com comentário opcional depois. Recusa,
    sem inferir o valor: interpolação ``${...}`` (o python-dotenv a expande, com
    ou sem aspas), barra invertida entre aspas simples ou duplas (escapes),
    aspas sem fechamento (valor em
    várias linhas), chave repetida com valores diferentes e linha não interpretável.
    """

    values: dict[str, str] = {}
    problems: list[tuple[int, str | None]] = []
    rejected: set[str] = set()
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = ENV_ASSIGNMENT.match(line)
        if not match:
            problems.append((number, None))
            continue
        key, rest = match.groups()
        value, ok = _env_value(rest)
        if not ok or (key in values and values[key] != value):
            problems.append((number, key))
            rejected.add(key)
            continue
        values[key] = value
    for key in rejected:
        values.pop(key, None)
    return values, problems


def _env_value(rest: str) -> tuple[str, bool]:
    if rest[:1] in {'"', "'"}:
        quote = rest[0]
        end = rest.find(quote, 1)
        if end == -1:
            return "", False
        value, tail = rest[1:end], rest[end + 1:].strip()
        if tail and not tail.startswith("#"):
            return "", False
        if "\\" in value or "${" in value:
            return "", False
        return value, True
    value = re.split(r"\s+#", rest, maxsplit=1)[0].strip()
    if "${" in value or '"' in value or "'" in value:
        return "", False
    return value, True


def parse_env_text(text: str) -> tuple[dict[str, str], list[int]]:
    """Valores aceitos e números das linhas recusadas (sem expor conteúdo)."""

    values, problems = _parse_env(text)
    return values, [number for number, _key in problems]


def _exact_values(env_paths: list[Path], keys: tuple[str, ...]) -> tuple[dict[str, str], dict, list[str]]:
    """Valores exatos em memória, resumo só com nomes/situações e motivos de incompletude."""

    exact: dict[str, str] = {}
    reasons: list[str] = []
    summary: dict = {"executado": False, "gramatica": "estrita-l1v2", "arquivos_env": [], "chaves": [],
                     "chaves_carregadas": [], "falhas": []}
    for index, env_path in enumerate(env_paths):
        label = f"env[{index}]:{env_path.parent.name}/{env_path.name}"
        if not env_path.is_file():
            summary["falhas"].append({"arquivo_env": label, "motivo": "ausente"})
            reasons.append("arquivo_env_ausente")
            continue
        try:
            raw = env_path.read_bytes()
            text = raw.decode("utf-8-sig")
        except (OSError, UnicodeError) as exc:
            summary["falhas"].append({"arquivo_env": label, "motivo": "ilegivel", "erro": _safe_error(exc)})
            reasons.append("arquivo_env_ilegivel")
            continue
        values, problems = _parse_env(text)
        summary["executado"] = True
        summary["arquivos_env"].append({
            "arquivo": label,
            "bom": raw.startswith(b"\xef\xbb\xbf"),
            "linhas_nao_suportadas": [number for number, _key in problems],
        })
        if problems:
            reasons.append("env_sintaxe_nao_suportada")
        unsupported = {key for _number, key in problems if key}
        for key in keys:
            value = values.get(key, "")
            if key in unsupported:
                situation = "nao_suportada"
            elif not value:
                situation = "ausente"
            elif is_placeholder(value):
                situation = "placeholder"
            elif len(value) < MIN_EXACT_LENGTH:
                situation = "curto"
            else:
                situation = "carregada"
                name = key if key not in exact or exact[key] == value else f"{key}#{index}"
                exact[name] = value
                if name not in summary["chaves_carregadas"]:
                    summary["chaves_carregadas"].append(name)
            summary["chaves"].append({"chave": key, "arquivo_env": label, "situacao": situation})
    if not summary["executado"]:
        reasons.append("modo_exato_nao_executado")
    return exact, summary, sorted(set(reasons))


# ─── Estrutura de resultado ──────────────────────────────────────────────────


class _TargetResult:
    """Acumula o resultado de um alvo; ``falhas_leitura`` torna o alvo incompleto."""

    def __init__(self) -> None:
        self.unidades_regras_projeto = 0
        self.unidades_detector = 0
        self.ocorrencias: list[dict] = []
        self.exclusoes: list[dict] = []
        self.falhas_leitura: list[dict] = []
        self.extras: dict = {}

    def as_dict(self) -> dict:
        status = "incompleto" if self.falhas_leitura else (
            "completo_com_ocorrencia" if self.ocorrencias else "completo_sem_ocorrencia"
        )
        return {
            "status": status,
            "unidades_regras_projeto": self.unidades_regras_projeto,
            "unidades_detector": self.unidades_detector,
            **self.extras,
            "ocorrencias": self.ocorrencias,
            "exclusoes": self.exclusoes,
            "falhas_leitura": self.falhas_leitura,
        }


class _Item:
    """Conteúdo a varrer num contexto de nome.

    ``rotulo`` é o caminho relativo (ou ``commit:``/``tag:``) usado como nome do
    arquivo para o detector; ``caminhos`` são todos os caminhos daquele contexto;
    ``regras_projeto`` indica se as regras independentes do nome rodam neste item
    (uma vez por conteúdo).
    """

    def __init__(self, rotulo: str, dados: bytes, blob: str | None = None,
                 caminhos: list[str] | None = None, regras_projeto: bool = True,
                 caminhos_conteudo: list[str] | None = None) -> None:
        self.rotulo = rotulo
        self.dados = dados
        self.blob = blob
        self.caminhos = caminhos
        self.regras_projeto = regras_projeto
        self.caminhos_conteudo = caminhos_conteudo or caminhos


def _base(item: _Item, caminhos: list[str] | None = None) -> dict:
    base: dict = {"arquivo": item.rotulo}
    if item.blob:
        base["blob"] = item.blob[:12]
    if caminhos is not None:
        base["caminhos"] = caminhos
    return base


# ─── Git ─────────────────────────────────────────────────────────────────────


def _git(repo: Path, *args: str, stdin: bytes | None = None) -> bytes:
    try:
        completed = subprocess.run(["git", "-C", str(repo), *args], input=stdin, capture_output=True, check=False)
    except OSError as exc:
        raise AuditError(f"git_{args[0]}_indisponivel") from exc
    if completed.returncode != 0:
        raise AuditError(f"git_{args[0]}_falhou:{completed.returncode}")
    return completed.stdout


def _cat_file_batch(repo: Path, object_ids: list[str]) -> dict[str, bytes | None]:
    """Lê objetos pelo ``git cat-file --batch``; ausentes voltam como ``None``."""

    if not object_ids:
        return {}
    raw = _git(repo, "cat-file", "--batch", stdin=("\n".join(object_ids) + "\n").encode())
    contents: dict[str, bytes | None] = {}
    position = 0
    try:
        for object_id in object_ids:
            header_end = raw.index(b"\n", position)
            header = raw[position:header_end].decode()
            position = header_end + 1
            if header.endswith(" missing"):
                contents[object_id] = None
                continue
            size = int(header.rsplit(" ", 1)[1])
            contents[object_id] = raw[position:position + size]
            position += size + 1
    except (ValueError, UnicodeError) as exc:
        raise AuditError("git_cat-file_saida_invalida") from exc
    return contents


def _index_entries(repo: Path) -> list[tuple[str, str, str]]:
    """(modo, blob, caminho) de cada entrada do índice."""

    entries = []
    for record in _git(repo, "ls-files", "-s", "-z").split(b"\0"):
        if not record:
            continue
        meta, path = record.split(b"\t", 1)
        mode, object_id, _stage = meta.decode().split()
        entries.append((mode, object_id, path.decode("utf-8", errors="surrogateescape")))
    return entries


def _worktree_paths(repo: Path) -> list[str]:
    raw = _git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    return sorted({path.decode("utf-8", errors="surrogateescape") for path in raw.split(b"\0") if path})


def _is_link(path: Path) -> bool:
    """Symlink, junction ou qualquer reparse point (inclui symlink do WSL no Windows)."""

    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(info.st_mode):
        return True
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(info, "st_file_attributes", 0) & reparse)


# ─── Varredura de conteúdo ───────────────────────────────────────────────────


def _load_detect_secrets() -> tuple[object | None, str | None]:
    try:
        import detect_secrets  # noqa: F401
        from detect_secrets.__version__ import VERSION
    except ImportError:
        return None, None
    return detect_secrets, VERSION


def _decode(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def _key(name: str) -> str:
    return os.path.normcase(os.path.normpath(name))


class _TrackedStream(io.StringIO):
    """Texto em memória que registra se o detector leu até o fim."""

    def __init__(self, text: str, files: "_MemoryFiles", key: str) -> None:
        super().__init__(text, newline=None)
        self._files = files
        self._key = key
        # RL1v3-02: com newline=None o buffer guarda o texto já normalizado (CRLF/CR -> LF);
        # o fim da leitura é medido nessa representação, não no texto original.
        self._length = len(self.getvalue())

    def _mark(self) -> None:
        if self.tell() >= self._length:
            self._files.completed.add(self._key)

    def read(self, size=-1):
        data = super().read(size)
        self._mark()
        return data

    def readline(self, size=-1):
        data = super().readline(size)
        self._mark()
        return data

    def readlines(self, hint=-1):
        data = super().readlines(hint)
        self._mark()
        return data

    def __next__(self):
        try:
            data = super().__next__()
        except StopIteration:
            self._files.completed.add(self._key)
            raise
        self._mark()
        return data


class _MemoryFiles:
    """Entrega ao detector o conteúdo em memória e registra o que ele leu.

    A versão 1.5.0 abre os arquivos com a codificação da localidade e descarta em
    silêncio falhas de leitura (``except IOError``), registrando-as apenas em log
    de nível WARNING, que o logger da biblioteca (ERROR) não entrega. Servindo o
    texto já decodificado, a leitura não depende da plataforma; e um arquivo só
    conta como processado se foi aberto, lido até o fim e as etapas supervisionadas
    do detector terminaram sem exceção (RL1v3-01: a falha é registrada antes de a
    biblioteca absorvê-la, sem depender do log). O aviso no log continua valendo
    como sinal adicional.
    """

    def __init__(self) -> None:
        self.contents: dict[str, str] = {}
        self.opened: set[str] = set()
        self.completed: set[str] = set()
        self.swallowed: set[str] = set()
        self.finished: set[str] = set()
        self.failed: set[str] = set()

    def processed(self, key: str) -> bool:
        return (key in self.opened and key in self.completed and key in self.finished
                and key not in self.failed and key not in self.swallowed)

    def open(self, file, mode="r", *args, **kwargs):
        key = _key(str(file))
        if key not in self.contents or "r" not in mode:
            raise FileNotFoundError("conteudo_nao_registrado")
        self.opened.add(key)
        stream = _TrackedStream(self.contents[key], self, key)
        stream.name = str(file)
        return stream


class _SwallowedReads(logging.Handler):
    def __init__(self, files: _MemoryFiles) -> None:
        super().__init__(logging.DEBUG)
        self.files = files

    def emit(self, record: logging.LogRecord) -> None:
        message = record.getMessage()
        if message.startswith("Unable to open file: "):
            self.files.swallowed.add(_key(message[len("Unable to open file: "):]))


def _supervised(files: _MemoryFiles, get_lines, process_lines):
    """Envolve as etapas que o ``scan_file`` protege com ``except IOError``.

    Qualquer exceção é registrada em ``files.failed`` e relançada, preservando o
    contrato da biblioteca. ``GeneratorExit`` é o encerramento antecipado legítimo
    (o detector achou segredo e parou); só então, ou no fim normal da leitura, a
    unidade conta como terminada.
    """

    def get_lines_supervised(filename):
        key = _key(str(filename))
        try:
            yield from get_lines(filename)
        except GeneratorExit:
            files.finished.add(key)
            raise
        except BaseException:
            files.failed.add(key)
            raise
        files.finished.add(key)

    def process_lines_supervised(lines, filename):
        try:
            yield from process_lines(lines=lines, filename=filename)
        except GeneratorExit:
            raise
        except BaseException:
            files.failed.add(_key(str(filename)))
            raise

    return get_lines_supervised, process_lines_supervised


@contextmanager
def _detector(files: _MemoryFiles):
    """Configura o detect-secrets só durante a auditoria e restaura tudo no fim."""

    from detect_secrets.core import scan
    from detect_secrets.settings import default_settings, get_settings

    handler = _SwallowedReads(files)
    previous = scan.__dict__.get("open")
    stages = (scan._get_lines_from_file, scan._process_line_based_plugins)
    log = scan.log
    saved = (log.level, log.propagate, log.disabled, list(log.handlers))
    with default_settings():
        get_settings().disable_filters(*DISABLED_FILTERS)
        scan.open = files.open
        scan._get_lines_from_file, scan._process_line_based_plugins = _supervised(files, *stages)
        log.setLevel(logging.WARNING)
        log.propagate = False
        log.disabled = False
        log.handlers[:] = [handler]
        try:
            yield
        finally:
            scan._get_lines_from_file, scan._process_line_based_plugins = stages
            log.handlers[:] = saved[3]
            log.setLevel(saved[0])
            log.propagate, log.disabled = saved[1], saved[2]
            if previous is None:
                scan.__dict__.pop("open", None)
            else:
                scan.open = previous


def _scan_items(items: list[_Item], exact: dict[str, str], result: _TargetResult, alvo: str) -> None:
    """Aplica as regras do projeto e o detect-secrets a cada item, sem gravar conteúdo."""

    from detect_secrets import SecretsCollection

    files = _MemoryFiles()
    pending: list[tuple[str, _Item, str]] = []
    for number, item in enumerate(items):
        base = _base(item)
        if len(item.dados) > MAX_BYTES:
            result.exclusoes.append({**base, "motivo": "acima_do_limite_de_tamanho"})
            continue
        if b"\0" in item.dados[:8192]:
            result.exclusoes.append({**base, "motivo": "binario"})
            continue
        text = _decode(item.dados)
        if item.regras_projeto:
            result.unidades_regras_projeto += 1
            paths = item.caminhos_conteudo if item.blob else None
            for line, rule in _project_rules(text, exact):
                result.ocorrencias.append({"alvo": alvo, **_base(item, paths), "linha": line,
                                           "regra": rule, "classe": CONTENT_CLASS})
            sql_paths = [p for p in (item.caminhos_conteudo or [item.rotulo]) if p.lower().endswith(".sql")]
            dump = DUMP_CONTENT.search(text)
            if sql_paths and dump:
                result.ocorrencias.append({"alvo": alvo, **_base(item, paths), "linha": _line_of(text, dump.start()),
                                           "regra": "dump_sql_por_conteudo", "classe": CONTENT_POLICY_CLASS})
        for number_line, line_text in enumerate(text.splitlines(), start=1):
            if ALLOWLIST_PRAGMA.search(line_text):
                result.exclusoes.append({**base, "linha": number_line, "motivo": "pragma_allowlist"})
        virtual = f"{number:06d}/{item.rotulo}"
        files.contents[_key(virtual)] = text
        pending.append((virtual, item, text))

    collection = SecretsCollection(root="")
    with _detector(files):
        for virtual, item, _text in pending:
            try:
                collection.scan_file(virtual)
            except Exception as exc:  # erro interno do detector: registrar sem mensagem
                result.falhas_leitura.append({**_base(item), "erro": f"detector:{_safe_error(exc)}"})
                continue
            key = _key(virtual)
            if not files.processed(key):
                result.falhas_leitura.append({**_base(item), "erro": "detector_nao_leu"})
                continue
            result.unidades_detector += 1
    by_virtual = {_key(virtual): item for virtual, item, _text in pending}
    for filename, secret in collection:
        item = by_virtual.get(_key(filename))
        if item is None:
            continue
        base = _base(item, item.caminhos if item.blob else None)
        if secret.secret_value is not None and is_placeholder(secret.secret_value):
            result.exclusoes.append({**_base(item), "linha": secret.line_number, "motivo": "placeholder"})
            continue
        result.ocorrencias.append({"alvo": alvo, **base, "linha": secret.line_number,
                                   "regra": f"detect-secrets:{secret.type}", "classe": CONTENT_CLASS})


# ─── Alvos ───────────────────────────────────────────────────────────────────


def _disk_link_target(root: Path, relative: str) -> str | None:
    path = root / relative
    if not _is_link(path):
        return None
    try:
        return os.readlink(path)
    except OSError:
        return "/<ilegivel>"


def _audit_worktree(repo: Path, paths: list[str], exact: dict[str, str], perfil: str) -> _TargetResult:
    result = _TargetResult()
    items: list[_Item] = []
    root_resolved = repo.resolve()
    link_cache: dict[str, bool] = {}

    def lookup(relative: str) -> str | None:
        return _disk_link_target(repo, relative)

    for relative in paths:
        base = {"arquivo": relative}
        try:
            parts = relative.split("/")
            crossing = None
            for size in range(1, len(parts)):
                prefix = "/".join(parts[:size])
                if prefix not in link_cache:
                    link_cache[prefix] = _is_link(repo / prefix)
                if link_cache[prefix]:
                    crossing = prefix
                    break
            if crossing:
                result.ocorrencias.append({"alvo": "arquivos", **base, "link": crossing,
                                           "regra": "caminho_atravessa_link", "classe": PATH_CLASS})
                continue
            path = repo / relative
            if _is_link(path):
                reason = link_chain_reason(relative, lookup, perfil)
                if reason:
                    result.ocorrencias.append({"alvo": "arquivos", **base, "regra": reason, "classe": PATH_CLASS})
                result.exclusoes.append({**base, "motivo": "link_nao_seguido"})
                continue
            if not path.exists():
                result.exclusoes.append({**base, "motivo": "ausente_no_disco"})
                continue
            if path.is_dir():
                result.exclusoes.append({**base, "motivo": "diretorio_ou_submodulo"})
                continue
            if not path.resolve(strict=True).is_relative_to(root_resolved):
                result.ocorrencias.append({"alvo": "arquivos", **base, "regra": "caminho_fora_da_raiz",
                                           "classe": PATH_CLASS})
                continue
            items.append(_Item(relative, path.read_bytes()))
        except OSError as exc:
            result.falhas_leitura.append({**base, "erro": _safe_error(exc)})
    _scan_items(items, exact, result, "arquivos")
    return result


def _audit_index(repo: Path, entries: list[tuple[str, str, str]], exact: dict[str, str], perfil: str) -> _TargetResult:
    result = _TargetResult()
    regular = [(object_id, path) for mode, object_id, path in entries if mode not in (SYMLINK_MODE, SUBMODULE_MODE)]
    links = {path: object_id for mode, object_id, path in entries if mode == SYMLINK_MODE}
    contents = _cat_file_batch(repo, sorted({object_id for object_id, _ in regular} | set(links.values())))
    targets: dict[str, str] = {}
    for path, object_id in links.items():
        data = contents.get(object_id)
        if data is None:
            result.falhas_leitura.append({"arquivo": path, "erro": "blob_ausente"})
            continue
        targets[path] = _decode(data)
    for path in sorted(targets):
        reason = link_chain_reason(path, targets.get, perfil)
        if reason:
            result.ocorrencias.append({"alvo": "indice", "arquivo": path, "regra": reason, "classe": PATH_CLASS})
        result.exclusoes.append({"arquivo": path, "motivo": "link_nao_seguido"})
    for mode, _object_id, path in entries:
        if mode == SUBMODULE_MODE:
            result.exclusoes.append({"arquivo": path, "motivo": "diretorio_ou_submodulo"})
    items: list[_Item] = []
    for object_id, path in regular:
        data = contents.get(object_id)
        if data is None:
            result.falhas_leitura.append({"arquivo": path, "erro": "blob_ausente"})
            continue
        items.append(_Item(path, data))
    _scan_items(items, exact, result, "indice")
    return result


def _resolve_refs(repo: Path, refs: list[str]) -> dict[str, dict[str, str]]:
    """Resolve cada ref para commit ou, se não houver commit, para árvore (instantâneo)."""

    resolved: dict[str, dict[str, str]] = {}
    for ref in refs:
        for kind in ("commit", "tree"):
            try:
                object_id = _git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{{kind}}}").decode().strip()
            except AuditError:
                continue
            resolved[ref] = {"tipo": kind, "objeto": object_id}
            break
        else:
            raise AuditError("ref_nao_resolvida")
    return resolved


class _History:
    """Tudo o que o histórico das refs contém, sem perder versões nem contextos."""

    def __init__(self) -> None:
        self.refs: dict[str, dict[str, str]] = {}
        self.commits: list[str] = []
        self.snapshots = 0
        self.blob_paths: dict[str, set[str]] = {}
        self.link_maps: set[tuple[tuple[str, str], ...]] = set()
        self.all_paths: set[str] = set()


def _history_tree(repo: Path, refs: list[str]) -> _History:
    history = _History()
    history.refs = _resolve_refs(repo, refs)
    heads = [item["objeto"] for item in history.refs.values() if item["tipo"] == "commit"]
    snapshots = [item["objeto"] for item in history.refs.values() if item["tipo"] == "tree"]
    history.commits = _git(repo, "rev-list", *heads).decode().split() if heads else []
    history.snapshots = len(snapshots)
    for tree in [*history.commits, *snapshots]:
        links: dict[str, str] = {}
        for record in _git(repo, "ls-tree", "-r", "-z", tree).split(b"\0"):
            if not record:
                continue
            meta, raw_path = record.split(b"\t", 1)
            mode, kind, object_id = meta.decode().split()
            path = raw_path.decode("utf-8", errors="surrogateescape")
            history.all_paths.add(path)
            if kind != "blob":
                continue
            if mode == SYMLINK_MODE:
                links[path] = object_id
            else:
                history.blob_paths.setdefault(object_id, set()).add(path)
        if links:
            history.link_maps.add(tuple(sorted(links.items())))
    return history


def _audit_history(repo: Path, refs: list[str], exact: dict[str, str], perfil: str) -> _TargetResult:
    result = _TargetResult()
    try:
        _collect_history(repo, refs, exact, perfil, result)
    except (AuditError, OSError, ValueError, UnicodeError) as exc:
        result.falhas_leitura.append({"arquivo": "historico", "erro": _safe_error(exc)})
    return result


def _collect_history(repo: Path, refs: list[str], exact: dict[str, str], perfil: str, result: _TargetResult) -> None:
    history = _history_tree(repo, refs)
    link_blobs = {object_id for link_map in history.link_maps for _path, object_id in link_map}
    contents = _cat_file_batch(repo, sorted(set(history.blob_paths) | link_blobs))
    findings: set[tuple[str, str, str]] = set()
    for link_map in history.link_maps:
        mapping = dict(link_map)
        targets = {path: _decode(contents[object_id]) for path, object_id in mapping.items()
                   if contents.get(object_id) is not None}
        for path, object_id in mapping.items():
            if path not in targets:
                result.falhas_leitura.append({"arquivo": path, "blob": object_id[:12], "erro": "blob_ausente"})
                continue
            reason = link_chain_reason(path, targets.get, perfil)
            if reason:
                findings.add((path, object_id, reason))
    for path, object_id, reason in sorted(findings):
        result.ocorrencias.append({"alvo": "historico", "arquivo": path, "blob": object_id[:12],
                                   "regra": reason, "classe": PATH_CLASS})
    items: list[_Item] = []
    for object_id, paths in sorted(history.blob_paths.items()):
        data = contents.get(object_id)
        ordered = sorted(paths)
        if data is None:
            result.falhas_leitura.append({"arquivo": ordered[0], "blob": object_id[:12], "erro": "blob_ausente"})
            continue
        contexts: dict[str, list[str]] = {}
        for path in ordered:
            contexts.setdefault(os.path.splitext(path)[1], []).append(path)
        for position, (_extension, group) in enumerate(sorted(contexts.items(), key=lambda kv: kv[1][0])):
            items.append(_Item(group[0], data, object_id, caminhos=group, regras_projeto=position == 0,
                               caminhos_conteudo=ordered))
    messages = _cat_file_batch(repo, history.commits)
    for commit in history.commits:
        raw = messages.get(commit)
        if raw is None:
            result.falhas_leitura.append({"arquivo": f"commit:{commit[:12]}", "erro": "commit_ausente"})
            continue
        items.append(_Item(f"commit:{commit[:12]}/MENSAGEM", raw.split(b"\n\n", 1)[-1]))
    tags = [ref for ref in history.refs if _git(repo, "cat-file", "-t", ref).decode().strip() == "tag"]
    for tag in tags:
        raw = _git(repo, "cat-file", "tag", tag)
        items.append(_Item(f"tag:{tag}/MENSAGEM", raw.split(b"\n\n", 1)[-1]))
    _scan_items(items, exact, result, "historico")
    result.extras.update({
        "refs": history.refs,
        "commits_examinados": len(history.commits),
        "instantaneos_examinados": history.snapshots,
        "blobs_distintos": len(history.blob_paths),
        "contextos_detector": sum(1 for item in items if item.blob),
        "mapas_de_links": len(history.link_maps),
        "mensagens_varridas": len(history.commits) + len(tags),
    })


def _audit_forbidden(sources: dict[str, set[str]], perfil: str) -> _TargetResult:
    result = _TargetResult()
    origins: dict[str, list[str]] = {}
    for origin, paths in sources.items():
        for path in paths:
            origins.setdefault(path, []).append(origin)
    result.extras["caminhos_avaliados"] = len(origins)
    for path in sorted(origins):
        reason = forbidden_reason(path, perfil)
        if reason:
            result.ocorrencias.append({"alvo": "proibidos", "arquivo": path, "regra": reason,
                                       "classe": PATH_CLASS, "origem": origins[path]})
    result.extras["origens"] = sorted(sources)
    return result


def _implementation(perfil: str) -> dict:
    return {
        "arquivo": "tools/security_audit.py",
        "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "versao_regras": RULES_VERSION,
        "perfil": perfil,
        "python": platform.python_version(),
        "plataforma": f"{platform.system()} {platform.release()} ({sys.platform})",
    }


def _run_target(report: dict, name: str, action) -> None:
    try:
        report["alvos"][name] = action().as_dict()
    except (AuditError, OSError, ValueError, UnicodeError) as exc:
        failed = _TargetResult()
        failed.falhas_leitura.append({"arquivo": name, "erro": _safe_error(exc)})
        report["alvos"][name] = failed.as_dict()


def _known_key(entry: dict) -> tuple:
    # A origem entra na chave: um caminho proibido revisado só no histórico não esconde
    # o mesmo caminho se ele voltar ao índice ou à árvore.
    # Na lista, o blob é gravado como "git:<hex>": o hexadecimal puro seria tomado pelo
    # detect-secrets como segredo de alta entropia.
    origem = entry.get("origem")
    blob = entry.get("blob")
    blob = blob.removeprefix("git:") if isinstance(blob, str) else blob
    return (entry.get("alvo"), entry.get("arquivo"), blob, entry.get("linha"), entry.get("regra"),
            tuple(sorted(origem)) if isinstance(origem, list) else None)


def load_known(path: Path) -> list[dict]:
    """Lê e valida a lista de ocorrências conhecidas; qualquer defeito é ``AuditError``."""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AuditError("conhecidas_ilegivel") from exc
    if not isinstance(data, dict) or data.get("versao") != 1 or not isinstance(data.get("ocorrencias"), list):
        raise AuditError("conhecidas_formato")
    entries = data["ocorrencias"]
    seen: set[tuple] = set()
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("alvo") not in ALL_TARGETS:
            raise AuditError("conhecidas_formato")
        if not all(isinstance(entry.get(field), str) and entry[field].strip()
                   for field in ("arquivo", "regra", "justificativa")):
            raise AuditError("conhecidas_sem_justificativa")
        if entry["regra"].startswith(NEVER_KNOWN):
            raise AuditError("conhecidas_regra_proibida")
        if entry.get("linha") is not None and not isinstance(entry["linha"], int):
            raise AuditError("conhecidas_formato")
        if entry.get("blob") is not None and not re.fullmatch(r"git:[0-9a-f]{12}", str(entry["blob"])):
            raise AuditError("conhecidas_formato")
        origem = entry.get("origem")
        if origem is not None and not (isinstance(origem, list) and origem
                                       and all(item in ("arquivos", "indice", "historico") for item in origem)):
            raise AuditError("conhecidas_formato")
        key = _known_key(entry)
        if key in seen:
            raise AuditError("conhecidas_duplicada")
        seen.add(key)
    return entries


def apply_known(report: dict, entries: list[dict]) -> None:
    """Separa as ocorrências revisadas; o status de cada alvo passa a contar só as novas."""

    known = {_known_key(entry) for entry in entries}
    used: set[tuple] = set()
    for data in report["alvos"].values():
        new, matched = [], []
        for occurrence in data["ocorrencias"]:
            key = _known_key(occurrence)
            (matched if key in known else new).append(occurrence)
            if key in known:
                used.add(key)
        data["ocorrencias"] = new
        data["ocorrencias_conhecidas"] = matched
        if data["status"] != "incompleto":
            data["status"] = "completo_com_ocorrencia" if new else "completo_sem_ocorrencia"
    report["conhecidas"]["aplicadas"] = len(used)
    report["conhecidas"]["nao_encontradas"] = [
        {field: entry.get(field) for field in ("alvo", "arquivo", "blob", "linha", "regra", "origem")}
        for entry in entries if _known_key(entry) not in used
    ]


def audit(
    root: Path = ROOT,
    targets: tuple[str, ...] = ALL_TARGETS,
    env_paths: list[Path] | None = None,
    refs: list[str] | None = None,
    keys: tuple[str, ...] = DEFAULT_KEYS,
    perfil: str = DEFAULT_PERFIL,
    known_path: Path | None = None,
) -> dict:
    """Executa a auditoria completa e devolve um relatório sem valores sensíveis."""

    unknown = sorted(set(targets) - set(ALL_TARGETS))
    if unknown:
        raise ValueError(f"alvos desconhecidos: {', '.join(unknown)}")
    _perfil(perfil)
    root = root.resolve()
    refs = refs or ["HEAD"]
    reasons: list[str] = []
    module, version = _load_detect_secrets()
    tool: dict = {"nome": "detect-secrets", "versao": version, "versao_esperada": DETECT_SECRETS_VERSION,
                  "filtros_desativados": sorted(DISABLED_FILTERS)}
    if module is None:
        reasons.append("detect_secrets_indisponivel")
    elif version != DETECT_SECRETS_VERSION:
        reasons.append("versao_detect_secrets_divergente")
    detector_ready = module is not None and version == DETECT_SECRETS_VERSION
    if detector_ready:
        from detect_secrets.settings import default_settings, get_settings

        with default_settings():
            get_settings().disable_filters(*DISABLED_FILTERS)
            tool["plugins"] = sorted(get_settings().plugins)
            tool["filtros"] = sorted(get_settings().filters)

    exact, exact_summary, exact_reasons = _exact_values([Path(p) for p in env_paths or []], keys)
    reasons.extend(exact_reasons)

    report: dict = {
        "tipo": "auditoria_segredos",
        "versao_regras": RULES_VERSION,
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "implementacao": _implementation(perfil),
        "repositorio": {"nome": root.name, "head": None},
        "ferramenta": tool,
        "modo_exato": exact_summary,
        "alvos": {},
    }
    try:
        report["repositorio"]["head"] = _git(root, "rev-parse", "HEAD").decode().strip()
        worktree = _worktree_paths(root)
        index = _index_entries(root)
        git_ready = True
    except (AuditError, OSError, ValueError, UnicodeError) as exc:
        reasons.append("repositorio_git_ilegivel")
        report["falha_repositorio"] = _safe_error(exc)
        worktree, index, git_ready = [], [], False

    content_ready = detector_ready and git_ready
    if content_ready and "arquivos" in targets:
        _run_target(report, "arquivos", lambda: _audit_worktree(root, worktree, exact, perfil))
    if content_ready and "indice" in targets:
        _run_target(report, "indice", lambda: _audit_index(root, index, exact, perfil))
    if content_ready and "historico" in targets:
        _run_target(report, "historico", lambda: _audit_history(root, refs, exact, perfil))
    if git_ready and "proibidos" in targets:
        def forbidden() -> _TargetResult:
            sources = {"arquivos": set(worktree), "indice": {path for _mode, _sha, path in index}}
            try:
                sources["historico"] = _history_tree(root, refs).all_paths
            except (AuditError, OSError, ValueError, UnicodeError) as exc:
                result = _audit_forbidden(sources, perfil)
                result.falhas_leitura.append({"arquivo": "historico", "erro": _safe_error(exc)})
                return result
            return _audit_forbidden(sources, perfil)

        _run_target(report, "proibidos", forbidden)

    if known_path is not None:
        report["conhecidas"] = {"arquivo": known_path.name}
        try:
            entries = load_known(known_path)
            report["conhecidas"].update(sha256=hashlib.sha256(known_path.read_bytes()).hexdigest(),
                                        entradas=len(entries))
            apply_known(report, entries)
        except (AuditError, OSError) as exc:
            reasons.append("lista_conhecidas_invalida")
            report["conhecidas"]["erro"] = _safe_error(exc)

    for target in targets:
        if target not in report["alvos"]:
            reasons.append(f"alvo_nao_executado:{target}")
        elif report["alvos"][target]["status"] == "incompleto":
            reasons.append(f"falha_leitura:{target}")
    found = any(data["ocorrencias"] for data in report["alvos"].values())
    report["status"] = "incompleto" if reasons else (
        "completo_com_ocorrencia" if found else "completo_sem_ocorrencia"
    )
    report["motivos_incompleto"] = sorted(set(reasons))
    report["resumo"] = {
        target: {"status": data["status"], "ocorrencias": len(data["ocorrencias"]),
                 "conhecidas": len(data.get("ocorrencias_conhecidas", []))}
        for target, data in report["alvos"].items()
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--env", type=Path, action="append",
                        help="Arquivo .env com os valores exatos (repetível na auditoria completa).")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--remediate", action="store_true", help="Substitui ocorrências exatas por placeholder.")
    parser.add_argument("--alvos", help="Ativa a auditoria completa: 'todos' ou lista com "
                                        "arquivos,indice,historico,proibidos.")
    parser.add_argument("--ref", action="append", default=[], help="Ref do histórico (repetível). Padrão: HEAD.")
    parser.add_argument("--perfil", choices=sorted(PERFIS), default=DEFAULT_PERFIL,
                        help="Regras de caminho: pre-merge (layout atual) ou monorepo (obrigatório a partir do L3).")
    parser.add_argument("--conhecidas", type=Path, default=None,
                        help="Lista de ocorrências conhecidas. Padrão: config/auditoria-ocorrencias-conhecidas.json "
                             "da raiz auditada, se existir.")
    parser.add_argument("--sem-conhecidas", action="store_true", help="Não aplica a lista de ocorrências conhecidas.")
    args = parser.parse_args(argv)
    if args.alvos:
        if args.remediate:
            parser.error("--remediate só existe no modo legado")
        targets = ALL_TARGETS if args.alvos == "todos" else tuple(t.strip() for t in args.alvos.split(",") if t.strip())
        known = None
        if not args.sem_conhecidas:
            padrao = args.root.resolve() / "config" / KNOWN_FILE.name
            known = args.conhecidas.resolve() if args.conhecidas else (padrao if padrao.is_file() else None)
        try:
            result = audit(args.root, targets, [p.resolve() for p in args.env or []], args.ref, perfil=args.perfil,
                           known_path=known)
            result["implementacao"]["argumentos"] = {
                "alvos": list(targets), "refs": args.ref or ["HEAD"], "perfil": args.perfil,
                "arquivos_env": len(args.env or []), "raiz": args.root.resolve().name,
                "conhecidas": known.name if known else None,
            }
        except Exception as exc:  # rede de segurança: nunca traceback nem mensagem bruta
            result = {"tipo": "auditoria_segredos", "versao_regras": RULES_VERSION, "status": "incompleto",
                      "motivos_incompleto": ["erro_inesperado"], "erro": type(exc).__name__}
        code = STATUS_EXIT[result["status"]]
    else:
        scanner = remediate_exact_secrets if args.remediate else scan_exact_secrets
        result = scanner(args.root.resolve(), args.env[0].resolve() if args.env else None)
        code = 0 if result["status"] == "sucesso" else 1
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
