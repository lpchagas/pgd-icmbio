"""Gate de liberação das três unidades piloto (plano de reorganização §7, L5).

Duas verificações:

- :func:`elegivel_para_liberacao` — há aceites válidos da **mesma identidade** nas
  três unidades piloto (CGOV, COCAGE e GR2) e uma deliberação de expansão?
- :func:`execucao_autorizada` — escopos piloto sempre podem ser executados; fora
  deles, produto **final ou compartilhável** exige elegibilidade de cada capacidade
  envolvida. Produto restrito, rascunho ou intermediário (A2) segue o uso restrito
  atual.

O gate é aplicado nos pontos oficiais (``lib.indicator_extraction``,
``gestao.runner``, ``relatorios.relatorio_v2``, ``relatorios.relatorio_cumulativo``
e ``lib.ciclo_gerencial``; as pontes antigas herdam). Os A1 continuam como
primitivas internas: não são canal de liberação, e a política não é barreira
técnica contra chamada direta.

Identidade do candidato: capacidade, versão de fórmula/contrato, fingerprint
(último commit que tocou as dependências + hash de cada dependência transitiva),
versão da política, versão do cadastro, escopo resolvido e referência à evidência.
A evidência aponta para o **ato humano** no acervo privado; o JSON não é assinatura.
"""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from lib.caminhos import PROJECT_ROOT
from lib.unidades_petrvs import carregar_hierarquia

CADASTRO = PROJECT_ROOT / "config" / "unidades-piloto.json"
ARQUIVO_ACEITES = PROJECT_ROOT / "artefatos_local" / "validacao" / "pilotos" / "aceites.json"
PACOTES_LOCAIS = ("lib", "relatorios", "gestao", "ocde", "mgi")

# Capacidades além dos alvos de TARGETS: os relatórios, com versão de contrato.
CAPACIDADES_RELATORIO = {
    "RELATORIO_V2": ("contrato-v2", PROJECT_ROOT / "relatorios" / "relatorio_v2.py"),
    "RELATORIO_CUMULATIVO": ("contrato-1", PROJECT_ROOT / "relatorios" / "relatorio_cumulativo.py"),
}


class LiberacaoRecusada(RuntimeError):
    """Execução fora dos pilotos, em produto final/compartilhável, sem elegibilidade."""


# --- Cadastro -----------------------------------------------------------------------------

@dataclass(frozen=True)
class Piloto:
    sigla: str
    id_petrvs: str | None
    conferido: bool
    seletor: str
    incluir_raiz: bool
    incluir_subordinadas: bool
    profundidade: int | None

    def seletor_cli(self) -> list[str]:
        return [f"--{self.seletor}", self.sigla]


@dataclass(frozen=True)
class Cadastro:
    versao: int
    politica: str
    pilotos: tuple[Piloto, ...]
    hierarquia_sha256: str | None

    @property
    def conferido(self) -> bool:
        return all(piloto.conferido for piloto in self.pilotos)


def carregar_cadastro(caminho: Path | None = None) -> Cadastro:
    """Lê e valida ``config/unidades-piloto.json``; cadastro inválido é erro."""

    caminho = caminho or CADASTRO
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cadastro de pilotos ilegível: {caminho.name}") from exc
    if not isinstance(dados.get("versao"), int) or not str(dados.get("politica") or "").strip():
        raise ValueError("Cadastro de pilotos sem 'versao' inteira ou sem 'politica'.")
    pilotos: list[Piloto] = []
    for item in dados.get("unidades", []):
        piloto = Piloto(
            sigla=str(item.get("sigla") or "").strip().upper(),
            id_petrvs=item.get("id_petrvs"),
            conferido=item.get("conferido") is True,
            seletor=str(item.get("seletor") or ""),
            incluir_raiz=item.get("incluir_raiz") is True,
            incluir_subordinadas=item.get("incluir_subordinadas") is True,
            profundidade=item.get("profundidade"),
        )
        _validar_piloto(piloto)
        pilotos.append(piloto)
    siglas = [piloto.sigla for piloto in pilotos]
    if len(pilotos) != 3 or len(set(siglas)) != 3:
        raise ValueError("O cadastro deve ter exatamente três unidades piloto distintas.")
    hierarquia = dados.get("hierarquia") or {}
    return Cadastro(dados["versao"], dados["politica"].strip(), tuple(pilotos), hierarquia.get("sha256"))


def _validar_piloto(piloto: Piloto) -> None:
    if not piloto.sigla:
        raise ValueError("Unidade piloto sem sigla.")
    if piloto.conferido and not piloto.id_petrvs:
        raise ValueError(f"Piloto {piloto.sigla} marcado como conferido sem id_petrvs.")
    # Só as combinações que o ScopeSpec resolve de fato: nunca outro recorte em silêncio.
    if piloto.seletor == "unidade":
        valido = piloto.incluir_raiz and not piloto.incluir_subordinadas and piloto.profundidade == 0
    elif piloto.seletor == "regional":
        valido = piloto.incluir_raiz and piloto.incluir_subordinadas and piloto.profundidade is None
    else:
        valido = False
    if not valido:
        raise ValueError(f"Configuração de escopo sem suporte no piloto {piloto.sigla}.")


def problemas_cadastro(cadastro: Cadastro) -> list[str]:
    """Conferência do cadastro na hierarquia atual: o id_petrvs é a raiz resolvida?"""

    from relatorios.escopo import EscopoInvalido, scope_from_values

    problemas = []
    for piloto in cadastro.pilotos:
        if not piloto.conferido:
            problemas.append(f"{piloto.sigla}: id_petrvs não conferido na fonte")
            continue
        try:
            raiz = scope_from_values(**{piloto.seletor: piloto.sigla}).ids[0]
        except EscopoInvalido as exc:
            problemas.append(f"{piloto.sigla}: {exc}")
            continue
        if raiz != piloto.id_petrvs:
            problemas.append(f"{piloto.sigla}: id_petrvs do cadastro difere da unidade resolvida no PETRVS")
    return problemas


def piloto_do_escopo(escopo: Any, cadastro: Cadastro) -> Piloto | None:
    """O piloto cujo recorte configurado é exatamente o escopo (tipo e sigla)."""

    for piloto in cadastro.pilotos:
        if escopo.kind == piloto.seletor and str(escopo.value).upper() == piloto.sigla:
            return piloto
    return None


# --- Identidade do candidato ----------------------------------------------------------------

def _sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _json_hash(valor: Any) -> str:
    return hashlib.sha256(json.dumps(valor, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _modulo_para_arquivo(modulo: str) -> Path | None:
    if not modulo or modulo.split(".", 1)[0] not in PACOTES_LOCAIS:
        return None
    base = PROJECT_ROOT.joinpath(*modulo.split("."))
    for candidato in (base.with_suffix(".py"), base / "__init__.py"):
        if candidato.is_file():
            return candidato
    return None


def _pacote_de(arquivo: Path) -> str:
    partes = arquivo.relative_to(PROJECT_ROOT).with_suffix("").parts
    return ".".join(partes[:-1])


def dependencias(entrypoint: Path) -> list[Path]:
    """Fechamento transitivo dos imports locais (lib, relatorios, gestao, ocde, mgi)."""

    vistos: set[Path] = set()
    pendentes = [entrypoint.resolve()]
    while pendentes:
        arquivo = pendentes.pop()
        if arquivo in vistos or not arquivo.is_file():
            continue
        vistos.add(arquivo)
        try:
            arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for no in ast.walk(arvore):
            nomes: list[str] = []
            if isinstance(no, ast.Import):
                nomes = [alias.name for alias in no.names]
            elif isinstance(no, ast.ImportFrom):
                base = no.module or ""
                if no.level:
                    pacote = _pacote_de(arquivo).split(".") if arquivo.is_relative_to(PROJECT_ROOT) else []
                    pacote = pacote[: len(pacote) - (no.level - 1)] if no.level > 1 else pacote
                    base = ".".join([*pacote, *([base] if base else [])])
                nomes = [base] + [f"{base}.{alias.name}" for alias in no.names]
            for nome in nomes:
                partes = nome.split(".")
                for fim in range(1, len(partes) + 1):  # pacotes intermediários também contam
                    destino = _modulo_para_arquivo(".".join(partes[:fim]))
                    if destino is not None:
                        pendentes.append(destino.resolve())
    return sorted(vistos)


def _git(*argumentos: str) -> str:
    try:
        resultado = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), *argumentos],
            capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
        )
    except OSError:
        return ""
    return resultado.stdout.strip() if resultado.returncode == 0 else ""


def capacidades_conhecidas() -> dict[str, tuple[str, Path]]:
    from lib.validation_contracts import TARGETS

    conhecidas = {codigo: (alvo.formula_version, alvo.production_entrypoint) for codigo, alvo in TARGETS.items()}
    conhecidas.update(CAPACIDADES_RELATORIO)
    return conhecidas


def fingerprint_candidato(capacidade: str) -> dict[str, Any]:
    """Commit que tocou por último as dependências + hash de cada uma."""

    conhecidas = capacidades_conhecidas()
    if capacidade not in conhecidas:
        raise ValueError(f"Capacidade desconhecida: {capacidade}")
    versao, entrypoint = conhecidas[capacidade]
    arquivos = dependencias(entrypoint)
    relativos = [arquivo.relative_to(PROJECT_ROOT).as_posix() for arquivo in arquivos]
    hashes = {rel: _sha256(arquivo) for rel, arquivo in zip(relativos, arquivos)}
    commit = _git("log", "-1", "--format=%H", "--", *relativos) or "sem-git"
    locais = bool(_git("status", "--porcelain", "--", *relativos))
    return {
        "capacidade": capacidade,
        "versao": versao,
        "commit": commit,
        "dependencias": hashes,
        "alteracoes_locais": locais,
        "fingerprint": _json_hash({"commit": commit, "dependencias": hashes}),
    }


def escopo_resolvido(piloto: Piloto) -> dict[str, Any]:
    """Lista ordenada de ids do PETRVS (raiz primeiro) e identidade da hierarquia usada."""

    from relatorios.escopo import scope_from_values

    spec = scope_from_values(**{piloto.seletor: piloto.sigla})
    hierarquia = carregar_hierarquia().sha256 or None
    return {"sigla": piloto.sigla, "seletor": piloto.seletor, "chave": spec.key,
            "ids": list(spec.ids), "hierarquia_sha256": hierarquia}


def identidade_candidato(capacidade: str, cadastro: Cadastro | None = None) -> dict[str, Any]:
    cadastro = cadastro or carregar_cadastro()
    impressao = fingerprint_candidato(capacidade)
    return {
        "capacidade": capacidade,
        "versao": impressao["versao"],
        "fingerprint": impressao["fingerprint"],
        "commit": impressao["commit"],
        "alteracoes_locais": impressao["alteracoes_locais"],
        "politica": cadastro.politica,
        "cadastro_versao": cadastro.versao,
    }


# --- Registro de aceites --------------------------------------------------------------------

def ler_registro(caminho: Path | None = None) -> dict[str, Any]:
    caminho = caminho or ARQUIVO_ACEITES
    if not caminho.is_file():
        return {"versao": 1, "aceites": [], "deliberacoes": []}
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    if not isinstance(dados.get("aceites"), list) or not isinstance(dados.get("deliberacoes"), list):
        raise ValueError("Registro de aceites corrompido.")
    return dados


def referencia_arquivo(caminho: Path) -> dict[str, str]:
    """Referência verificável a um arquivo do acervo privado (caminho relativo + hash)."""

    from tools.security_audit import is_private_path

    absoluto = caminho.resolve()
    if not absoluto.is_file():
        raise ValueError(f"Arquivo de evidência inexistente: {caminho.name}")
    try:
        relativo = absoluto.relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("A evidência deve estar no acervo privado do projeto.") from exc
    if not is_private_path(relativo):
        raise ValueError("A evidência deve estar em área privada (nunca versionada).")
    return {"caminho": relativo, "sha256": _sha256(absoluto)}


def _problema_referencia(ref: Any, nome: str) -> str | None:
    if not isinstance(ref, dict) or not ref.get("caminho") or not ref.get("sha256"):
        return f"{nome} ausente"
    caminho = PROJECT_ROOT / ref["caminho"]
    if not caminho.is_file():
        return f"{nome} ausente: {ref['caminho']}"
    if _sha256(caminho) != ref["sha256"]:
        return f"{nome} corrompida: {ref['caminho']}"
    return None


def problema_manifesto(caminho: Path, capacidade: str, chave: str) -> str | None:
    """Manifesto de aceite: execução nova, integrada, bem-sucedida, no escopo do piloto."""

    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "manifesto ilegível"
    if dados.get("modo") == "fixture" or "fixture" in str(dados.get("tipo", "")):
        return "manifesto gerado por fixture"
    if dados.get("reutilizado") or dados.get("retomado") or "consolidado" in str(dados.get("tipo", "")):
        return "manifesto não vem de execução nova do candidato"
    if dados.get("rascunho") is True:
        return "manifesto de rascunho"
    escopo = dados.get("escopo") or {}
    if not isinstance(escopo, dict) or escopo.get("chave") != chave:
        return "manifesto de outro escopo"
    if capacidade not in CAPACIDADES_RELATORIO:
        if dados.get("tipo") != "protocolo_validacao_A1_A5" or dados.get("modo") != "integrado":
            return "manifesto não é validação integrada A1–A5"
        if dados.get("status_global") != "sucesso":
            return "manifesto sem sucesso global"
        resultados = [r for r in dados.get("resultados", []) if r.get("alvo") == capacidade]
        if not resultados or any(r.get("status") in ("falha", "pendente") for r in resultados):
            return "manifesto sem resultado aprovado da capacidade"
    return None


def _mesma_identidade(registro: dict[str, Any], identidade: dict[str, Any]) -> str | None:
    for campo, rotulo in (("capacidade", "capacidade"), ("versao", "versão"), ("politica", "política"),
                          ("cadastro_versao", "versão do cadastro"), ("fingerprint", "fingerprint")):
        if registro.get(campo) != identidade.get(campo):
            if campo == "fingerprint" and registro.get("versao") == identidade.get("versao"):
                return "mesma versão de fórmula com fingerprint diferente"
            return f"candidato diferente ({rotulo})"
    return None


def elegivel_para_liberacao(
    identidade: dict[str, Any],
    *,
    cadastro: Cadastro | None = None,
    registro: dict[str, Any] | None = None,
) -> tuple[bool, list[str]]:
    """Três aceites válidos da mesma identidade (um por piloto) e deliberação de expansão."""

    cadastro = cadastro or carregar_cadastro()
    try:
        registro = registro if registro is not None else ler_registro()
    except (OSError, ValueError, json.JSONDecodeError):
        return False, ["registro de aceites corrompido"]
    capacidade = identidade["capacidade"]
    motivos: list[str] = []
    for piloto in cadastro.pilotos:
        candidatos = [a for a in registro["aceites"] if a.get("capacidade") == capacidade and a.get("piloto") == piloto.sigla]
        if not candidatos:
            motivos.append(f"{piloto.sigla}: sem aceite registrado")
            continue
        atual = None
        falhas: list[str] = []
        for aceite in candidatos:
            if aceite.get("revogado"):
                falhas.append("aceite revogado")
                continue
            problema = _mesma_identidade(aceite, identidade)
            if problema is None:
                if atual is None:
                    atual = escopo_resolvido(piloto)
                esperado = aceite.get("escopo_resolvido") or {}
                if esperado.get("ids") != atual["ids"] or esperado.get("hierarquia_sha256") != atual["hierarquia_sha256"]:
                    problema = "escopo resolvido mudou (hierarquia ou subordinação)"
            problema = problema or _problema_referencia(aceite.get("evidencia"), "evidência")
            problema = problema or _problema_referencia(aceite.get("manifesto"), "manifesto")
            if problema is None and aceite.get("manifesto"):
                problema = problema_manifesto(PROJECT_ROOT / aceite["manifesto"]["caminho"], capacidade, atual["chave"])
            if problema is None:
                break
            falhas.append(problema)
        else:
            motivos.append(f"{piloto.sigla}: " + "; ".join(sorted(set(falhas))))
    deliberacoes = [d for d in registro["deliberacoes"] if d.get("capacidade") == capacidade and not d.get("revogado")]
    if not any(_mesma_identidade(d, identidade) is None and _problema_referencia(d.get("evidencia"), "evidência") is None
               for d in deliberacoes):
        motivos.append("sem deliberação de expansão válida para esta identidade")
    return not motivos, motivos


# --- Autorização nos pontos oficiais --------------------------------------------------------

@dataclass(frozen=True)
class Decisao:
    comando: str
    escopo: str
    produto: str
    final: bool
    autorizada: bool
    motivo: str
    piloto: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def execucao_autorizada(
    comando: str,
    escopo: Any,
    produto: str,
    *,
    capacidades: Iterable[str] = (),
    final: bool = False,
    cadastro: Cadastro | None = None,
) -> Decisao:
    """Pilotos sempre; fora deles, produto final/compartilhável exige elegibilidade."""

    cadastro = cadastro or carregar_cadastro()
    piloto = piloto_do_escopo(escopo, cadastro)
    base = {"comando": comando, "escopo": escopo.key, "produto": produto, "final": final}
    if piloto is not None:
        return Decisao(**base, autorizada=True, motivo="escopo piloto", piloto=piloto.sigla)
    if not final and produto != "compartilhavel":
        return Decisao(**base, autorizada=True, motivo="uso restrito atual (produto não final nem compartilhável)")
    registro_cache: dict[str, Any] | None = None
    motivos: list[str] = []
    for capacidade in capacidades:
        if registro_cache is None:
            try:
                registro_cache = ler_registro()
            except (OSError, ValueError, json.JSONDecodeError):
                return Decisao(**base, autorizada=False, motivo="registro de aceites corrompido")
            if not registro_cache["aceites"]:
                return Decisao(**base, autorizada=False,
                               motivo="fora dos pilotos sem aceites registrados (expansão depende de três aceites e deliberação)")
        elegivel, faltas = elegivel_para_liberacao(identidade_candidato(capacidade, cadastro),
                                                   cadastro=cadastro, registro=registro_cache)
        if not elegivel:
            motivos.append(f"{capacidade}: " + " | ".join(faltas))
    if registro_cache is None:
        return Decisao(**base, autorizada=False, motivo="fora dos pilotos sem capacidade elegível declarada")
    if motivos:
        return Decisao(**base, autorizada=False, motivo="; ".join(motivos))
    return Decisao(**base, autorizada=True, motivo="capacidades elegíveis para liberação")


def exigir_execucao_autorizada(comando: str, escopo: Any, produto: str, **opcoes: Any) -> dict[str, Any]:
    """Como :func:`execucao_autorizada`, mas recusa com :class:`LiberacaoRecusada`."""

    decisao = execucao_autorizada(comando, escopo, produto, **opcoes)
    if not decisao.autorizada:
        raise LiberacaoRecusada(
            f"{comando}: execução recusada para o escopo {decisao.escopo} em produto "
            f"{'final' if decisao.final else decisao.produto}: {decisao.motivo}"
        )
    return decisao.as_dict()
