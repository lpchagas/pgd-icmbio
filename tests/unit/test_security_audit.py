from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


MODULE = Path(__file__).resolve().parents[2] / "tools" / "security_audit.py"
SPEC = importlib.util.spec_from_file_location("security_audit", MODULE)
security_audit = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(security_audit)

AWS_KEY = "AKIAIOSFODNN7ZQWRTPY"  # pragma: allowlist secret
ENV_PASSWORD = "senha-local-exclusiva-da-fixture"  # pragma: allowlist secret
MARCADOR = "MARCADOR-SENSIVEL-DE-TESTE"


def _cpf_com_digitos(base: str) -> str:
    """Monta um CPF válido em tempo de execução: nenhum CPF válido fica literal no repositório."""

    digits = [int(char) for char in base]
    for size in (9, 10):
        total = sum(digit * weight for digit, weight in zip(digits, range(size + 1, 1, -1)))
        digits.append((total * 10) % 11 % 10)
    raw = "".join(map(str, digits))
    return f"{raw[:3]}.{raw[3:6]}.{raw[6:9]}-{raw[9:]}"


CPF_VALIDO = _cpf_com_digitos("987654321")


# ─── Modo legado ─────────────────────────────────────────────────────────────


def test_exact_secret_scan_never_returns_secret(tmp_path):
    secret = "valor-secreto-apenas-fixture"  # pragma: allowlist secret
    env = tmp_path / ".env"
    env.write_text(f"DENODO_PASSWORD={secret}\n", encoding="utf-8")
    (tmp_path / "doc.md").write_text(f"acidente: {secret}\n", encoding="utf-8")
    result = security_audit.scan_exact_secrets(tmp_path, env, ("DENODO_PASSWORD",))
    assert result["status"] == "falha"
    assert result["ocorrencias_fora_do_armazenamento"][0]["arquivo"] == "doc.md"
    assert secret not in str(result)


def test_env_is_an_authorized_location(tmp_path):
    env = tmp_path / ".env"
    env.write_text("DENODO_PASSWORD=segredo-local\n", encoding="utf-8")
    result = security_audit.scan_exact_secrets(tmp_path, env, ("DENODO_PASSWORD",))
    assert result["status"] == "sucesso"


def test_remediation_replaces_only_external_occurrence_and_preserves_env(tmp_path):
    secret = "valor-secreto-remediacao"  # pragma: allowlist secret
    env = tmp_path / ".env"
    exposed = tmp_path / "legacy.md"
    env.write_text(f"DENODO_PASSWORD={secret}\n", encoding="utf-8")
    exposed.write_text(f"legado: {secret}\n", encoding="utf-8")
    result = security_audit.remediate_exact_secrets(tmp_path, env, ("DENODO_PASSWORD",))
    assert result["status"] == "sucesso"
    assert result["arquivos_sanitizados"] == ["legacy.md"]
    assert secret in env.read_text(encoding="utf-8")
    assert secret not in exposed.read_text(encoding="utf-8")


def test_legacy_dotenv_semantics_are_preserved(tmp_path):
    """RL1-04: o parser legado continua como era; só o modo novo usa a gramática estrita."""

    env = tmp_path / ".env"
    env.write_text('A="valor" # comentario\nexport B=x\n', encoding="utf-8")
    assert security_audit._dotenv(env) == {"A": 'valor" # comentario', "export B": "x"}


# ─── Auxiliares da auditoria completa ────────────────────────────────────────


def _git(repo: Path, *args: str, stdin: str | None = None) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
         "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false", "-c", "core.symlinks=false", *args],
        input=stdin, capture_output=True, text=True, check=True,
    )
    return completed.stdout.strip()


def _repo(tmp_path: Path, files: dict[str, str], message: str = "inicial") -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    for relative, content in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _git(repo, "add", "-A", "-f")
    _git(repo, "commit", "-q", "-m", message)
    return repo


def _env(tmp_path: Path, content: str | None = None) -> Path:
    env = tmp_path / "privado" / ".env"
    env.parent.mkdir(exist_ok=True)
    env.write_text(content or f"DENODO_PASSWORD={ENV_PASSWORD}\nDENODO_USER=seu_cpf_aqui\n", encoding="utf-8")
    return env


def _index_link(repo: Path, path: str, target: str) -> None:
    blob = _git(repo, "hash-object", "-w", "--stdin", stdin=target)
    _git(repo, "update-index", "--add", "--cacheinfo", f"120000,{blob},{path}")


def _rules(report: dict, target: str) -> list[tuple[str, str]]:
    return [(item["arquivo"], item["regra"]) for item in report["alvos"][target]["ocorrencias"]]


def _dir_link(link: Path, target: Path) -> None:
    """Junction no Windows (não exige privilégio); symlink de diretório no POSIX."""

    if os.name == "nt":
        import _winapi

        _winapi.CreateJunction(str(target), str(link))
    else:
        link.symlink_to(target, target_is_directory=True)


# ─── Contrato geral ──────────────────────────────────────────────────────────


def test_clean_repository_with_placeholders_is_complete_without_occurrence(tmp_path):
    repo = _repo(tmp_path, {
        ".env.example": "DENODO_PASSWORD=sua_senha_aqui\nMYSQL_PASSWORD=defina-a-senha-local\n",  # pragma: allowlist secret
        "docs/seguranca.md": "Configure DENODO_PASSWORD e MYSQL_PASSWORD no .env local.\n"
                             'Exemplo: password = "sua_senha_aqui"\n',
        "lib/modulo.py": "VALOR = 1\n",
    })
    report = security_audit.audit(repo, env_paths=[_env(tmp_path)])
    assert report["status"] == "completo_sem_ocorrencia", report["motivos_incompleto"]
    assert report["modo_exato"]["chaves_carregadas"] == ["DENODO_PASSWORD"]
    assert {"chave": "DENODO_USER", "situacao": "placeholder"} in [
        {"chave": item["chave"], "situacao": item["situacao"]} for item in report["modo_exato"]["chaves"]
    ]
    assert set(report["alvos"]) == set(security_audit.ALL_TARGETS)


def test_report_identifies_the_implementation_that_produced_it(tmp_path):
    repo = _repo(tmp_path, {"lib/modulo.py": "VALOR = 1\n"})
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    implementation = report["implementacao"]
    assert implementation["sha256"] == hashlib.sha256(MODULE.read_bytes()).hexdigest()
    assert implementation["versao_regras"] == security_audit.RULES_VERSION
    assert implementation["perfil"] == "pre-merge"
    assert {"python", "plataforma"} <= set(implementation)


def test_secret_is_reported_by_path_and_line_without_value_or_hash(tmp_path):
    repo = _repo(tmp_path, {
        "config.py": f'# conexão\naws_key = "{AWS_KEY}"\nsenha = "{ENV_PASSWORD}"\ncpf = "{CPF_VALIDO}"\n',
    })
    report = security_audit.audit(repo, env_paths=[_env(tmp_path)])
    rendered = json.dumps(report, ensure_ascii=False)
    assert report["status"] == "completo_com_ocorrencia"
    rules = {(item["linha"], item["regra"], item["classe"]) for item in report["alvos"]["arquivos"]["ocorrencias"]}
    assert (2, "detect-secrets:AWS Access Key", "conteudo_sensivel") in rules
    assert (3, "valor_exato:DENODO_PASSWORD", "conteudo_sensivel") in rules
    assert (4, "cpf_valido", "conteudo_sensivel") in rules
    for sensitive in (AWS_KEY, ENV_PASSWORD, CPF_VALIDO, "hashed_secret"):
        assert sensitive not in rendered


def test_allowlist_pragma_is_recorded_as_exclusion(tmp_path):
    pragma = "# pragma: " + "allowlist secret"
    repo = _repo(tmp_path, {"lib/fixture.py": f'CHAVE = "{AWS_KEY}"  {pragma}\n'})
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    assert report["alvos"]["arquivos"]["ocorrencias"] == []
    assert report["alvos"]["arquivos"]["exclusoes"] == [
        {"arquivo": "lib/fixture.py", "linha": 1, "motivo": "pragma_allowlist"},
    ]


def test_without_exact_mode_the_audit_is_incomplete_never_success(tmp_path):
    repo = _repo(tmp_path, {"lib/modulo.py": "VALOR = 1\n"})
    report = security_audit.audit(repo)
    assert report["status"] == "incompleto"
    assert "modo_exato_nao_executado" in report["motivos_incompleto"]
    assert security_audit.main(["--root", str(repo), "--alvos", "todos"]) == 2


def test_index_is_read_from_blobs_not_from_disk(tmp_path):
    repo = _repo(tmp_path, {"lib/modulo.py": "VALOR = 1\n"})
    (repo / "lib" / "modulo.py").write_text(f'chave = "{AWS_KEY}"\n', encoding="utf-8")
    _git(repo, "add", "lib/modulo.py")
    (repo / "lib" / "modulo.py").write_text("VALOR = 2\n", encoding="utf-8")
    report = security_audit.audit(repo, ("arquivos", "indice"), env_paths=[_env(tmp_path)])
    assert report["alvos"]["arquivos"]["ocorrencias"] == []
    assert _rules(report, "indice") == [("lib/modulo.py", "detect-secrets:AWS Access Key")]


def test_history_finds_removed_secret_and_commit_message(tmp_path):
    repo = _repo(tmp_path, {"notas.md": f"chave antiga {AWS_KEY}\n", "docs/.env": "X=1\n"})
    (repo / "notas.md").write_text("sem segredo\n", encoding="utf-8")
    _git(repo, "rm", "-q", "docs/.env")
    _git(repo, "commit", "-q", "-am", f"remove chave; senha era {ENV_PASSWORD}")
    report = security_audit.audit(repo, ("arquivos", "historico", "proibidos"), env_paths=[_env(tmp_path)])
    assert report["alvos"]["arquivos"]["ocorrencias"] == []
    history = report["alvos"]["historico"]
    assert history["commits_examinados"] == 2
    assert ("notas.md", "detect-secrets:AWS Access Key") in _rules(report, "historico")
    assert any(label.startswith("commit:") and rule == "valor_exato:DENODO_PASSWORD"
               for label, rule in _rules(report, "historico"))
    forbidden = report["alvos"]["proibidos"]["ocorrencias"]
    assert forbidden == [{"alvo": "proibidos", "arquivo": "docs/.env", "regra": "credencial_env",
                          "classe": "politica_caminho", "origem": ["historico"]}]


def test_tree_ref_snapshot_is_scanned_without_commits(tmp_path):
    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})
    (repo / "agente").mkdir()
    (repo / "agente" / "AGENTS.md").write_text(f"chave {AWS_KEY}\n", encoding="utf-8")
    _git(repo, "add", "-f", "agente/AGENTS.md")
    tree = _git(repo, "write-tree")
    _git(repo, "update-ref", "refs/codex/checkpoint", tree)
    _git(repo, "rm", "-q", "--cached", "agente/AGENTS.md")
    report = security_audit.audit(repo, ("historico", "proibidos"), env_paths=[_env(tmp_path)],
                                  refs=["refs/codex/checkpoint"])
    history = report["alvos"]["historico"]
    assert history["refs"]["refs/codex/checkpoint"]["tipo"] == "tree"
    assert (history["commits_examinados"], history["instantaneos_examinados"]) == (0, 1)
    assert _rules(report, "historico") == [("agente/AGENTS.md", "detect-secrets:AWS Access Key")]
    assert ("agente/AGENTS.md", "instrucao_aninhada") in _rules(report, "proibidos")


def test_unknown_ref_makes_history_incomplete(tmp_path):
    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})
    report = security_audit.audit(repo, ("historico",), env_paths=[_env(tmp_path)], refs=["nao-existe"])
    assert report["alvos"]["historico"]["status"] == "incompleto"
    assert report["status"] == "incompleto"


def test_unreadable_file_makes_the_target_incomplete(tmp_path, monkeypatch):
    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n", "lib/b.py": "B = 2\n"})
    original = Path.read_bytes

    def fail_on_b(self):
        if self.name == "b.py":
            raise PermissionError("negado")
        return original(self)

    monkeypatch.setattr(Path, "read_bytes", fail_on_b)
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    assert report["alvos"]["arquivos"]["status"] == "incompleto"
    assert report["alvos"]["arquivos"]["falhas_leitura"] == [{"arquivo": "lib/b.py", "erro": "PermissionError"}]
    assert report["status"] == "incompleto"


def test_missing_env_file_makes_the_audit_incomplete(tmp_path):
    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})
    report = security_audit.audit(repo, ("arquivos",), env_paths=[tmp_path / "inexistente" / ".env"])
    assert report["status"] == "incompleto"
    assert "arquivo_env_ausente" in report["motivos_incompleto"]


def test_non_ascii_text_is_scanned_in_utf8(tmp_path):
    repo = _repo(tmp_path, {"docs/area.md": f"Área Ídolo Ðelta\nchave = \"{AWS_KEY}\"\n"})
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    assert _rules(report, "arquivos") == [("docs/area.md", "detect-secrets:AWS Access Key")]


# ─── RL1-01 — links e limites da raiz ────────────────────────────────────────


def test_rl1_01_parent_directory_link_is_not_followed(tmp_path, monkeypatch):
    repo = _repo(tmp_path, {"docs/x.py": "VALOR = 1\n", "lib/a.py": "A = 1\n"})
    externo = tmp_path / "externo"
    externo.mkdir()
    (externo / "x.py").write_text(f'chave = "{AWS_KEY}"\n', encoding="utf-8")
    shutil.rmtree(repo / "docs")
    _dir_link(repo / "docs", externo)
    lidos: list[Path] = []
    original = Path.read_bytes

    def record(self):
        lidos.append(self)
        return original(self)

    monkeypatch.setattr(Path, "read_bytes", record)
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    assert not any(externo.resolve() in path.resolve().parents or path.resolve() == externo.resolve()
                   for path in lidos if path.name == "x.py")
    rules = _rules(report, "arquivos")
    assert ("docs/x.py", "caminho_atravessa_link") in rules
    assert all(rule != "detect-secrets:AWS Access Key" for _path, rule in rules)


@pytest.mark.parametrize(("link", "target", "reason"), [
    ("docs/atalho", "../cgov/x", "symlink_para_caminho_proibido:area_privada"),
    ("docs/atalho", "../.env", "symlink_para_caminho_proibido:credencial_env"),
    ("docs/atalho", "../AGENTS.md", "symlink_para_instrucao"),                 # instrução da raiz só como arquivo
    ("docs/atalho", "sub/CLAUDE.md", "symlink_para_caminho_proibido:instrucao_aninhada"),
    ("CLAUDE.md", "docs/instrucoes.md", "instrucao_como_link"),
    ("agente/AGENTS.md", "../AGENTS.md", "instrucao_como_link"),
    ("docs/atalho", "../../fora", "symlink_fora_da_raiz"),
    ("docs/atalho", "/mnt/c/projetos/x", "symlink_absoluto"),
    ("docs/atalho", "C:\\Users\\x", "symlink_absoluto"),
    ("docs/atalho", "../lib/modulo.py", None),
])
def test_symlink_reason(link, target, reason):
    assert security_audit.symlink_reason(link, target) == reason


def test_symlink_to_private_area_is_refused_from_the_index(tmp_path):
    repo = _repo(tmp_path, {"docs/README.md": "# Docs\n"})
    _index_link(repo, "docs/atalho", "../cgov/analises")
    report = security_audit.audit(repo, ("indice",), env_paths=[_env(tmp_path)])
    assert _rules(report, "indice") == [("docs/atalho", "symlink_para_caminho_proibido:area_privada")]


def test_rl1_01_link_chains_and_cycles_are_resolved_inside_the_index(tmp_path):
    repo = _repo(tmp_path, {"docs/README.md": "# Docs\n"})
    _index_link(repo, "docs/a", "b")
    _index_link(repo, "docs/b", "../cgov/x")
    _index_link(repo, "docs/c", "d")
    _index_link(repo, "docs/d", "c")
    _index_link(repo, "docs/e", "sub/x")
    _index_link(repo, "docs/sub", "../setup")
    report = security_audit.audit(repo, ("indice",), env_paths=[_env(tmp_path)])
    rules = set(_rules(report, "indice"))
    assert ("docs/a", "symlink_para_caminho_proibido:area_privada") in rules
    assert ("docs/b", "symlink_para_caminho_proibido:area_privada") in rules
    assert ("docs/c", "symlink_ciclo") in rules
    assert ("docs/e", "symlink_para_caminho_proibido:area_privada") in rules


# ─── RL1-02 — falhas e três estados ──────────────────────────────────────────


def test_rl1_02_read_failure_inside_detector_is_not_success(tmp_path, monkeypatch):
    from detect_secrets.core import scan

    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})

    def fail(*_args, **_kwargs):
        raise OSError("leitura interrompida")

    monkeypatch.setattr(scan, "_get_lines_from_file", fail)
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    assert report["alvos"]["arquivos"]["status"] == "incompleto"
    assert report["status"] == "incompleto"
    assert "open" not in scan.__dict__


def test_rl1_02_unreadable_env_gives_structured_incomplete(tmp_path, monkeypatch):
    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})
    env = _env(tmp_path)
    for name in ("read_bytes", "read_text"):
        original = getattr(Path, name)

        def fail(self, *args, _original=original, **kwargs):
            if self.name == ".env":
                raise PermissionError(MARCADOR)
            return _original(self, *args, **kwargs)

        monkeypatch.setattr(Path, name, fail)
    report = security_audit.audit(repo, ("arquivos",), env_paths=[env])
    assert report["status"] == "incompleto"
    assert "arquivo_env_ilegivel" in report["motivos_incompleto"]
    assert MARCADOR not in json.dumps(report)


@pytest.mark.parametrize(("subcommand", "targets"), [
    ("cat-file", ("indice",)),
    ("ls-tree", ("historico",)),
    ("ls-files", ("arquivos",)),
])
def test_rl1_02_git_failure_in_each_phase_is_incomplete_without_raw_stderr(tmp_path, monkeypatch, subcommand, targets):
    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})
    original = security_audit.subprocess.run

    def run(command, *args, **kwargs):
        if command[0] == "git" and subcommand in command:
            return subprocess.CompletedProcess(command, 128, b"", f"fatal: {MARCADOR}\n".encode())
        return original(command, *args, **kwargs)

    monkeypatch.setattr(security_audit.subprocess, "run", run)
    report = security_audit.audit(repo, targets, env_paths=[_env(tmp_path)])
    assert report["status"] == "incompleto"
    assert MARCADOR not in json.dumps(report)


def test_rl1_02_divergent_library_version_does_not_run_the_detector(tmp_path, monkeypatch):
    import detect_secrets

    repo = _repo(tmp_path, {"lib/a.py": f'k = "{AWS_KEY}"\n'})
    calls: list[str] = []
    monkeypatch.setattr(security_audit, "_load_detect_secrets", lambda: (detect_secrets, "0.0.0"))
    monkeypatch.setattr(detect_secrets.SecretsCollection, "scan_file", lambda self, name: calls.append(name))
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    assert report["status"] == "incompleto"
    assert "versao_detect_secrets_divergente" in report["motivos_incompleto"]
    assert calls == []


def test_rl1_02_missing_library_is_incomplete(tmp_path, monkeypatch):
    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})
    monkeypatch.setattr(security_audit, "_load_detect_secrets", lambda: (None, None))
    report = security_audit.audit(repo, env_paths=[_env(tmp_path)])
    assert report["status"] == "incompleto"
    assert "detect_secrets_indisponivel" in report["motivos_incompleto"]


def test_rl1_02_unexpected_error_in_main_is_json_incomplete(tmp_path, monkeypatch, capsys):
    def explode(*_args, **_kwargs):
        raise ValueError(MARCADOR)

    monkeypatch.setattr(security_audit, "audit", explode)
    assert security_audit.main(["--root", str(tmp_path), "--alvos", "todos"]) == 2
    printed = capsys.readouterr().out
    assert json.loads(printed)["status"] == "incompleto"
    assert MARCADOR not in printed


def test_rl1_02_detector_open_is_restored_after_an_exception(tmp_path, monkeypatch):
    from detect_secrets import SecretsCollection
    from detect_secrets.core import scan

    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})

    def explode(self, name):
        raise RuntimeError("falha interna")

    monkeypatch.setattr(SecretsCollection, "scan_file", explode)
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    assert report["status"] == "incompleto"
    assert "open" not in scan.__dict__


# ─── RL1-03 — cobertura histórica ────────────────────────────────────────────


def test_rl1_03_every_version_of_a_history_link_is_checked(tmp_path):
    repo = _repo(tmp_path, {"lib/modulo.py": "A = 1\n"})
    _index_link(repo, "docs/atalho", "../lib/modulo.py")
    _git(repo, "commit", "-q", "-m", "link seguro")
    _index_link(repo, "docs/atalho", "../cgov/analises")
    _git(repo, "commit", "-q", "-m", "link alterado")
    _index_link(repo, "docs/atalho", "../lib/modulo.py")
    _git(repo, "commit", "-q", "-m", "link restaurado")
    report = security_audit.audit(repo, ("historico",), env_paths=[_env(tmp_path)])
    assert ("docs/atalho", "symlink_para_caminho_proibido:area_privada") in _rules(report, "historico")


def test_rl1_03_shared_blob_keeps_every_path_context(tmp_path):
    content = f'chave = "{AWS_KEY}"\n'
    repo = _repo(tmp_path, {"a.lock": content, "b.py": content})
    report = security_audit.audit(repo, ("historico",), env_paths=[_env(tmp_path)])
    found = [item for item in report["alvos"]["historico"]["ocorrencias"]
             if item["regra"] == "detect-secrets:AWS Access Key"]
    assert found
    paths = {path for item in found for path in item["caminhos"]}
    assert {"a.lock", "b.py"} <= paths


def test_rl1_03_renamed_file_keeps_both_paths(tmp_path):
    repo = _repo(tmp_path, {"antigo.md": f"chave {AWS_KEY}\n"})
    _git(repo, "mv", "antigo.md", "novo.md")
    _git(repo, "commit", "-q", "-m", "renomeia")
    report = security_audit.audit(repo, ("historico",), env_paths=[_env(tmp_path)])
    paths = {path for item in report["alvos"]["historico"]["ocorrencias"] for path in item["caminhos"]}
    assert {"antigo.md", "novo.md"} <= paths


# ─── RL1-04 — interpretação do .env ──────────────────────────────────────────


def test_rl1_04_supported_env_syntax_loads_the_consumer_value(tmp_path):
    env = _env(tmp_path, "\ufeffexport DENODO_PASSWORD=\"senha-com-aspas-fixture\" # comentario\n"
                         "DENODO_USER=usuario-fixture-123 # comentario\n"
                         "MYSQL_PASSWORD='simples-fixture'\n"  # pragma: allowlist secret
                         "# DENODO_PASS=comentada-fixture\n")
    repo = _repo(tmp_path, {"vazou.md": "senha-com-aspas-fixture\nusuario-fixture-123\nsimples-fixture\n"})
    report = security_audit.audit(repo, ("arquivos",), env_paths=[env])
    assert report["status"] == "completo_com_ocorrencia", report["motivos_incompleto"]
    assert set(_rules(report, "arquivos")) == {
        ("vazou.md", "valor_exato:DENODO_PASSWORD"),
        ("vazou.md", "valor_exato:DENODO_USER"),
        ("vazou.md", "valor_exato:MYSQL_PASSWORD"),
    }
    situations = {item["chave"]: item["situacao"] for item in report["modo_exato"]["chaves"]}
    assert situations["DENODO_PASS"] == "ausente"
    assert report["modo_exato"]["arquivos_env"][0]["bom"] is True


@pytest.mark.parametrize("line", [
    "DENODO_PASSWORD=${OUTRA_VARIAVEL}",
    'DENODO_PASSWORD="com\\nescape"',  # pragma: allowlist secret
    'DENODO_PASSWORD="abre sem fechar',
    "linha sem atribuicao",
])
def test_rl1_04_unsupported_env_syntax_is_refused_as_incomplete(tmp_path, line):
    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path, line + "\n")])
    assert report["status"] == "incompleto"
    assert "env_sintaxe_nao_suportada" in report["motivos_incompleto"]
    assert "OUTRA_VARIAVEL" not in json.dumps(report)


def test_rl1_04_parser_distinguishes_key_situations():
    values, lines = security_audit.parse_env_text(
        "DENODO_USER=seu_cpf_aqui\nDENODO_PASSWORD=abc\nMYSQL_PASSWORD=${X}\nANTHROPIC_API_KEY=valor-real-fixture\n"
    )
    assert lines == [3]
    assert values["ANTHROPIC_API_KEY"] == "valor-real-fixture"  # pragma: allowlist secret
    assert "MYSQL_PASSWORD" not in values


# ─── RL1-05 — filtros e exclusões ────────────────────────────────────────────


def test_rl1_05_name_based_filters_do_not_hide_content(tmp_path):
    content = f'{{"chave": "{AWS_KEY}"}}\n'
    names = ("normal.json", "package-lock.json", "swagger.txt", "deps.lock", "estilo.css")
    repo = _repo(tmp_path, dict.fromkeys(names, content))
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    found = {path for path, rule in _rules(report, "arquivos") if rule == "detect-secrets:AWS Access Key"}
    assert found == set(names)
    target = report["alvos"]["arquivos"]
    assert target["unidades_detector"] == target["unidades_regras_projeto"] == len(names)
    assert report["ferramenta"]["filtros_desativados"] == sorted(security_audit.DISABLED_FILTERS)


def test_rl1_05_binary_is_recorded_and_not_counted_as_scanned(tmp_path):
    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})
    (repo / "imagem.png").write_bytes(b"\x89PNG\x00\x00" + AWS_KEY.encode())
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    target = report["alvos"]["arquivos"]
    assert {"arquivo": "imagem.png", "motivo": "binario"} in target["exclusoes"]
    assert target["unidades_detector"] == 1


# ─── RL1-06 — arquivos privados e proibidos ──────────────────────────────────


@pytest.mark.parametrize(("path", "perfil", "reason"), [
    (".env", "pre-merge", "credencial_env"),
    ("agente/.env.local", "pre-merge", "credencial_env"),
    ("docs/.envrc", "pre-merge", "credencial_env"),
    (".env.example", "pre-merge", None),
    ("docs/.env.example", "pre-merge", None),
    ("config/pgd_agente_root.cnf", "pre-merge", "credencial_cnf"),
    ("AGENTS.md", "pre-merge", None),                                   # H1/L4d: raiz comum versionada
    ("CLAUDE.md", "monorepo", None),
    ("PROJECT.md", "monorepo", None),
    ("docs/agente/AGENTS.md", "pre-merge", "instrucao_aninhada"),
    ("agente/CLAUDE.md", "monorepo", "instrucao_aninhada"),              # raiz de componente não é a raiz comum
    ("agente/PROJECT.md", "pre-merge", "instrucao_aninhada"),
    ("x/.claude/y.md", "pre-merge", "area_privada"),
    ("docs/artefatos_local/z.md", "pre-merge", "area_privada"),
    ("artefatos_local/ocde/x.md", "pre-merge", "area_privada"),
    ("data/backups/x.txt", "pre-merge", "area_privada"),
    ("agente/data/backups/x.txt", "pre-merge", None),
    ("agente/data/backups/x.txt", "monorepo", "area_privada"),
    ("agente/testes_cgov/s01.md", "monorepo", "area_privada"),
    ("testes_cgov/s01.md", "pre-merge", "area_privada"),
    ("src/dados/schema.sql", "pre-merge", None),
    ("src/dados/schema.sql", "monorepo", "sql_fora_da_excecao"),
    ("agente/dados/schema.sql", "monorepo", None),
    ("agente/dados/schema.sql", "pre-merge", "sql_fora_da_excecao"),
    ("agente/dados/migracoes/001_inicial.sql", "monorepo", None),
    ("agente/dados/extra.sql", "monorepo", "sql_fora_da_excecao"),
    ("agente/dados/pgd_agente_20260901.sql", "monorepo", "dump_sql"),
    ("backup.sql.gz", "pre-merge", "dump_sql"),
    ("docs/referencias-pgd/README.md", "pre-merge", None),
    ("docs/referencias-pgd/portaria.pdf", "pre-merge", "acervo_referencias_privado"),
    ("consultas_denodo.ipynb", "pre-merge", "notebook_com_resultado"),
    ("consultas_denodo_template.ipynb", "pre-merge", None),
    ("docs/apresentacao.pptx", "pre-merge", "documento_nao_versionavel"),
    ("tests/fixtures/ok.csv", "pre-merge", None),
    ("relatorio.csv", "pre-merge", "planilha_fora_de_fixture"),
    ("docs/README.md", "pre-merge", None),
])
def test_forbidden_reason(path, perfil, reason):
    assert security_audit.forbidden_reason(path, perfil) == reason


def test_forbidden_file_inside_allowed_folder_is_refused(tmp_path):
    repo = _repo(tmp_path, {
        "agente/dados/schema.sql": "CREATE TABLE t (id INT);\n",
        "agente/dados/migracoes/001_inicial.sql": "SELECT 1;\n",
        "agente/dados/pgd_agente_20260901.sql": "-- dump\n",
        "agente/dados/migracoes/002_backup.dump.sql": "-- dump\n",
        "docs/referencias-pgd/README.md": "# Referências\n",
        "docs/referencias-pgd/01/norma.md": "texto normativo\n",
        "tests/fixtures/ok.csv": "a|b\n",
        "relatorio.csv": "a|b\n",
    })
    report = security_audit.audit(repo, ("proibidos",), env_paths=[_env(tmp_path)], perfil="monorepo")
    found = {(item["arquivo"], item["regra"]) for item in report["alvos"]["proibidos"]["ocorrencias"]}
    assert found == {
        ("agente/dados/pgd_agente_20260901.sql", "dump_sql"),
        ("agente/dados/migracoes/002_backup.dump.sql", "dump_sql"),
        ("docs/referencias-pgd/01/norma.md", "acervo_referencias_privado"),
        ("relatorio.csv", "planilha_fora_de_fixture"),
    }
    assert {item["classe"] for item in report["alvos"]["proibidos"]["ocorrencias"]} == {"politica_caminho"}


def test_rl1_06_dump_disguised_as_migration_is_found_by_content(tmp_path):
    repo = _repo(tmp_path, {"agente/dados/migracoes/001_backup.sql":
                            "-- MySQL dump 10.13  Distrib 8.4.9\nINSERT INTO t VALUES (1);\n"})
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)], perfil="monorepo")
    assert ("agente/dados/migracoes/001_backup.sql", "dump_sql_por_conteudo") in _rules(report, "arquivos")


def test_unknown_profile_is_refused():
    with pytest.raises(ValueError):
        security_audit.forbidden_reason("x", "outro")


def test_cpf_rule_accepts_only_valid_check_digits():
    digits = CPF_VALIDO.replace(".", "").replace("-", "")
    assert security_audit.cpf_is_valid(CPF_VALIDO)
    assert security_audit.cpf_is_valid(digits)
    assert not security_audit.cpf_is_valid(digits[:-1] + str((int(digits[-1]) + 1) % 10))
    assert not security_audit.cpf_is_valid("1" * 11)



# ─── RL1v2-01 — falha absorvida depois da abertura ───────────────────────────


@pytest.mark.parametrize("level", ["WARNING", "ERROR"])
@pytest.mark.parametrize("read_chars", [0, 1])
def test_rl1v2_01_failure_after_open_is_not_complete(tmp_path, monkeypatch, level, read_chars):
    import logging

    from detect_secrets.core import scan

    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})

    def fail_after_open(filename):
        with scan.open(filename) as stream:
            if read_chars:
                stream.read(read_chars)
            raise OSError(MARCADOR)
        yield []

    monkeypatch.setattr(scan, "_get_lines_from_file", fail_after_open)
    saved = (scan.log.level, scan.log.propagate, scan.log.disabled)
    handlers = list(scan.log.handlers)
    scan.log.setLevel(getattr(logging, level))
    try:
        report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
        assert (scan.log.level, scan.log.propagate, scan.log.disabled) == (getattr(logging, level), saved[1], saved[2])
        assert scan.log.handlers == handlers
    finally:
        scan.log.setLevel(saved[0])
    target = report["alvos"]["arquivos"]
    assert target["status"] == "incompleto"
    assert target["unidades_detector"] == 0
    assert target["falhas_leitura"][0]["erro"] == "detector_nao_leu"
    assert MARCADOR not in json.dumps(report)
    assert "open" not in scan.__dict__


def test_rl1v2_01_file_read_to_the_end_is_counted(tmp_path):
    repo = _repo(tmp_path, {"vazio.txt": "", "lib/a.py": "A = 1\n", "dados.json": '{"a": 1}\n'})
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    target = report["alvos"]["arquivos"]
    assert target["status"] == "completo_sem_ocorrencia", target["falhas_leitura"]
    assert target["unidades_detector"] == 3


# ─── RL1v2-02 — aspas simples e o python-dotenv ──────────────────────────────


@pytest.mark.parametrize("line", [
    "DENODO_PASSWORD='${OUTRA_VARIAVEL}'",
    "DENODO_PASSWORD='com\\barra'",  # pragma: allowlist secret
    "DENODO_PASSWORD='com\'aspa'",  # pragma: allowlist secret
    'DENODO_PASSWORD="${OUTRA_VARIAVEL}"',
    "DENODO_PASSWORD=${OUTRA_VARIAVEL}",
])
def test_rl1v2_02_interpolation_and_escapes_are_refused_with_any_quote(tmp_path, line):
    values, refused = security_audit.parse_env_text(line + "\n")
    assert refused == [1]
    assert values == {}
    repo = _repo(tmp_path, {"lib/a.py": "A = 1\n"})
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path, line + "\n")])
    assert report["status"] == "incompleto"
    assert "env_sintaxe_nao_suportada" in report["motivos_incompleto"]


@pytest.mark.parametrize("line", [
    "DENODO_PASSWORD=valor-fixture-simples",  # pragma: allowlist secret
    'DENODO_PASSWORD="valor fixture duplas"',  # pragma: allowlist secret
    "DENODO_PASSWORD='valor fixture simples'",  # pragma: allowlist secret
    "export DENODO_PASSWORD='valor#fixture'",  # pragma: allowlist secret
    "DENODO_PASSWORD=valor-fixture # comentario",
])
def test_rl1v2_02_accepted_syntax_matches_python_dotenv(line):
    dotenv = pytest.importorskip("dotenv")
    values, refused = security_audit.parse_env_text(line + "\n")
    assert refused == []
    assert values == dict(dotenv.dotenv_values(stream=io.StringIO(line + "\n")))


# ─── RL1v2-03 — componentes de link resolvidos em sequência ──────────────────


def test_rl1v2_03_link_through_intermediate_link_escaping_root_is_reported():
    links = {"docs/bridge": "../safe", "docs/link": "bridge/../../external.txt"}
    assert security_audit.link_chain_reason("docs/link", links.get) == "symlink_fora_da_raiz"


@pytest.mark.parametrize(("links", "start", "reason"), [
    ({"docs/a": "../safe/x.txt"}, "docs/a", None),
    ({"docs/bridge": "../safe", "docs/link": "bridge/x.txt"}, "docs/link", None),
    ({"docs/bridge": "../safe", "docs/link": "bridge/../y.txt"}, "docs/link", None),
    ({"docs/bridge": "../safe", "docs/link": "bridge/../../../x"}, "docs/link", "symlink_fora_da_raiz"),
    ({"docs/bridge": "../cgov", "docs/link": "bridge/x.txt"}, "docs/link",
     "symlink_para_caminho_proibido:area_privada"),
    ({"docs/bridge": "../safe", "docs/link": "bridge/../cgov/x"}, "docs/link",
     "symlink_para_caminho_proibido:area_privada"),
    ({"docs/c": "d", "docs/d": "c"}, "docs/c", "symlink_ciclo"),
    ({"docs/bridge": "/etc", "docs/link": "bridge/x"}, "docs/link", "symlink_absoluto"),
    ({"a/b": "../c", "c/d": "../a/b/../z"}, "c/d", None),
    ({"docs/a": "../AGENTS.md"}, "docs/a", "symlink_para_instrucao"),
    ({"docs/bridge": "..", "docs/link": "bridge/PROJECT.md"}, "docs/link", "symlink_para_instrucao"),
    ({"CLAUDE.md": "docs/x.md"}, "CLAUDE.md", "instrucao_como_link"),
])
def test_rl1v2_03_sequential_resolution_table(links, start, reason):
    assert security_audit.link_chain_reason(start, links.get) == reason


def test_rl1v2_03_index_and_history_use_their_own_link_map(tmp_path):
    repo = _repo(tmp_path, {"safe/x.txt": "x\n", "docs/README.md": "# Docs\n"})
    _index_link(repo, "docs/bridge", "../safe")
    _index_link(repo, "docs/link", "bridge/../../external.txt")
    _git(repo, "commit", "-q", "-m", "links")
    _git(repo, "rm", "-q", "--cached", "docs/link", "docs/bridge")
    report = security_audit.audit(repo, ("indice", "historico"), env_paths=[_env(tmp_path)])
    assert ("docs/link", "symlink_fora_da_raiz") in _rules(report, "historico")
    assert ("docs/link", "symlink_fora_da_raiz") not in _rules(report, "indice")
    _index_link(repo, "docs/bridge", "../safe")
    _index_link(repo, "docs/link", "bridge/../../external.txt")
    report = security_audit.audit(repo, ("indice",), env_paths=[_env(tmp_path)])
    assert ("docs/link", "symlink_fora_da_raiz") in _rules(report, "indice")


def test_rl1v2_03_disk_link_through_intermediate_link_is_reported_without_reading(tmp_path, monkeypatch):
    repo = _repo(tmp_path, {"safe/x.txt": "x\n", "docs/README.md": "# Docs\n"})
    (tmp_path / "external.txt").write_text(f'chave = "{AWS_KEY}"\n', encoding="utf-8")
    try:
        os.symlink("../safe", repo / "docs" / "bridge", target_is_directory=True)
        os.symlink("bridge/../../external.txt", repo / "docs" / "link")
    except (OSError, NotImplementedError):
        pytest.skip("symlink indisponivel neste ambiente")
    lidos: list[str] = []
    original = Path.read_bytes

    def record(self):
        lidos.append(self.name)
        return original(self)

    monkeypatch.setattr(Path, "read_bytes", record)
    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    assert ("docs/link", "symlink_fora_da_raiz") in _rules(report, "arquivos")
    assert "external.txt" not in lidos


# ─── RL1v2-04 — extensões distintas não se fundem no histórico ───────────────


def test_rl1v2_04_same_blob_with_different_extension_case_keeps_each_context(tmp_path):
    content = "password = hunter2hunter2xyz\n"  # pragma: allowlist secret
    individual = {}
    for name in ("a.py", "z.PY"):
        item = security_audit._Item(name, content.encode())
        target = security_audit._TargetResult()
        security_audit._scan_items([item], {}, target, "historico")
        individual[name] = [o["regra"] for o in target.ocorrencias]
    assert individual["a.py"] == []
    assert individual["z.PY"] == ["detect-secrets:Secret Keyword"]
    repo = _repo(tmp_path, {"a.py": content, "z.PY": content})
    report = security_audit.audit(repo, ("historico",), env_paths=[_env(tmp_path)])
    found = [o for o in report["alvos"]["historico"]["ocorrencias"] if o["regra"] == "detect-secrets:Secret Keyword"]
    assert found
    assert {path for item in found for path in item["caminhos"]} == {"z.PY"}
    assert report["alvos"]["historico"]["contextos_detector"] == 2


# ─── RL1v3-01 — falha absorvida sem depender do log ──────────────────────────


def _repo_exato(tmp_path: Path, files: dict[str, str]) -> Path:
    """Como _repo, mas grava os bytes exatos: no Windows, write_text trocaria LF por CRLF."""

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    for relative, content in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8"))
    _git(repo, "add", "-A", "-f")
    _git(repo, "commit", "-q", "-m", "inicial")
    return repo


class _BloqueiaTudo:
    def filter(self, record):
        return False


@pytest.mark.parametrize("supressao", ["disable_global", "filtro_no_logger"])
@pytest.mark.parametrize("momento", ["antes_de_abrir", "leitura_parcial", "leitura_total", "etapa_plugins"])
def test_rl1v3_01_falha_absorvida_nunca_vira_sucesso(tmp_path, monkeypatch, supressao, momento):
    import logging

    from detect_secrets.core import scan

    repo = _repo_exato(tmp_path, {"lib/a.py": "A = 1\nB = 2\n"})
    originais = (scan._get_lines_from_file, scan._process_line_based_plugins)

    def obter_linhas(filename):
        if momento == "antes_de_abrir":
            raise OSError(MARCADOR)
        with scan.open(filename) as stream:
            stream.read(1) if momento == "leitura_parcial" else stream.read()
            if momento != "etapa_plugins":
                raise OSError(MARCADOR)
        yield ["A = 1\n", "B = 2\n"]

    def plugins(lines, filename):
        if momento == "etapa_plugins":
            raise OSError(MARCADOR)
        yield from ()

    monkeypatch.setattr(scan, "_get_lines_from_file", obter_linhas)
    monkeypatch.setattr(scan, "_process_line_based_plugins", plugins)
    filtro = _BloqueiaTudo()
    if supressao == "disable_global":
        logging.disable(logging.CRITICAL)
    else:
        scan.log.addFilter(filtro)
    try:
        report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    finally:
        logging.disable(logging.NOTSET)
        scan.log.removeFilter(filtro)

    target = report["alvos"]["arquivos"]
    assert (target["status"], target["unidades_detector"]) == ("incompleto", 0)
    assert target["falhas_leitura"][0]["erro"] == "detector_nao_leu"
    assert security_audit.STATUS_EXIT[report["status"]] == 2
    assert MARCADOR not in json.dumps(report)
    assert (scan._get_lines_from_file, scan._process_line_based_plugins) == (obter_linhas, plugins)
    assert "open" not in scan.__dict__
    monkeypatch.undo()
    assert (scan._get_lines_from_file, scan._process_line_based_plugins) == originais


def test_rl1v3_01_encerramento_antecipado_por_segredo_conta_como_processado(tmp_path):
    segredo = "AKIA" + "IOSFODNN7EXAMPLF"  # formato AWS sintético  # pragma: allowlist secret
    repo = _repo_exato(tmp_path, {"lib/a.py": f"CHAVE = '{segredo}'\nOUTRA = 1\n"})

    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])

    target = report["alvos"]["arquivos"]
    assert target["unidades_detector"] == 1 and not target["falhas_leitura"]
    assert target["status"] == "completo_com_ocorrencia"


# ─── RL1v3-02 — quebras de linha não viram falso incompleto ──────────────────


@pytest.mark.parametrize("quebra", ["\n", "\r\n", "\r", "misto"])
def test_rl1v3_02_formatos_validos_com_qualquer_quebra_sao_processados(tmp_path, quebra):
    def texto(linhas):
        if quebra == "misto":
            return "".join(l + ("\r\n", "\n", "\r")[i % 3] for i, l in enumerate(linhas))
        return "".join(l + quebra for l in linhas)

    arquivos = {
        "config.yaml": texto(["chave: valor", "lista:", "  - a"]),
        "config.yml": texto(["chave: valor"]),
        "segredo.eyaml": texto(["chave: valor"]),
        "swagger.yaml": texto(["openapi: 3.0.0"]),
        "dados.json": texto(['{"a": 1,', '"b": 2}']),
        "config.ini": texto(["[secao]", "chave = valor"]),
        "notas.txt": texto(["linha um", "linha dois"]),
        "vazio.txt": "",
        "so_quebra.txt": "\r\n" if quebra == "\r\n" else "\n",
        "sem_quebra_final.txt": "unica linha",
    }
    repo = _repo_exato(tmp_path, arquivos)

    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])

    target = report["alvos"]["arquivos"]
    assert target["falhas_leitura"] == [], target["falhas_leitura"]
    assert target["unidades_detector"] == len(arquivos)
    assert target["status"] == "completo_sem_ocorrencia"


def test_rl1v3_02_leitura_parcial_com_crlf_continua_incompleta(tmp_path, monkeypatch):
    from detect_secrets.core import scan

    repo = _repo_exato(tmp_path, {"config.yaml": "chave: valor\r\noutra: 2\r\n"})

    def le_parte(filename):
        with scan.open(filename) as stream:
            stream.readline()
        yield ["chave: valor\n"]

    monkeypatch.setattr(scan, "_get_lines_from_file", le_parte)

    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])

    target = report["alvos"]["arquivos"]
    assert (target["status"], target["unidades_detector"]) == ("incompleto", 0)


# ─── RL1v2-06 — política de caminhos única e raiz de componente ──────────────


@pytest.mark.parametrize(("path", "perfil", "reason"), [
    ("docs/AGENTS.md/info.txt", "pre-merge", "instrucao_aninhada"),         # nome de instrução como pasta
    ("CLAUDE.md/info.txt", "monorepo", "instrucao_aninhada"),               # pasta na raiz também
    ("docs/sub/CLAUDE.md", "pre-merge", "instrucao_aninhada"),
    ("agente/.github/skills/a.py", "monorepo", "area_privada"),              # raiz de componente
    ("agente/.github/skills/a.py", "pre-merge", None),                       # antes do merge, agente/ não é componente
    (".github/skills/a.py", "monorepo", "area_privada"),
    (".github/workflows/quality.yml", "monorepo", None),
    ("agente/.github/workflows/ci.yml", "monorepo", None),
    ("docs/cgov/README.md", "pre-merge", None),                              # cgov só é privada na raiz
    ("agente/docs/referencias-pgd/norma.pdf", "monorepo", "acervo_referencias_privado"),  # local intermediário do L3
    ("agente/docs/referencias-pgd/README.md", "monorepo", None),
])
def test_rl1v2_06_fronteiras_da_politica_de_caminhos(path, perfil, reason):
    assert security_audit.forbidden_reason(path, perfil) == reason


def test_rl1v2_06_verificador_e_teste_documental_usam_a_mesma_politica():
    from tools import verificar_links

    caminhos = [
        "artefatos_local/x.md", "docs/artefatos_local/x.md", ".claude/skills/a.md", "cgov/analises/run.py",
        "docs/cgov/README.md", "setup/configurar_env.ps1", "CLAUDE.md", "docs/AGENTS.md/info.txt",
        ".env", ".env.example", "docs/referencias-pgd/norma.md", "docs/referencias-pgd/README.md",
        "relatorio.csv", "docs/README.md",
    ]
    for caminho in caminhos:
        esperado = security_audit.forbidden_reason(caminho) in security_audit.PRIVACY_REASONS
        assert verificar_links._privado(tuple(caminho.split("/"))) is esperado, caminho
        assert security_audit.is_private_path(caminho) is esperado, caminho
    assert not security_audit.is_private_path("relatorio.csv")  # não versionável, mas não é área privada
    # L4d: links públicos para as instruções da raiz são aceitos; para as aninhadas, não.
    assert not any(security_audit.is_private_path(nome, "monorepo") for nome in ("CLAUDE.md", "AGENTS.md", "PROJECT.md"))
    assert security_audit.is_private_path("agente/AGENTS.md", "monorepo")


# ─── L4e — ocorrências conhecidas (histórico mantido, H9) ────────────────────


def _conhecidas(tmp_path: Path, entradas: list[dict]) -> Path:
    arquivo = tmp_path / "conhecidas.json"
    arquivo.write_text(json.dumps({"versao": 1, "ocorrencias": entradas}), encoding="utf-8")
    return arquivo


def _entrada(ocorrencia: dict, justificativa: str = "fixture sintética revisada") -> dict:
    entrada = {**{k: ocorrencia.get(k) for k in ("alvo", "arquivo", "blob", "linha", "regra")},
               "justificativa": justificativa}
    if entrada["blob"]:
        entrada["blob"] = f"git:{entrada['blob']}"
    return entrada


def test_l4e_conhecida_separada_e_status_so_conta_novas(tmp_path):
    repo = _repo(tmp_path, {"docs/a.md": f"chave = \"{AWS_KEY}\"\n", "docs/b.md": "# ok\n"})
    base = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])
    [ocorrencia] = base["alvos"]["arquivos"]["ocorrencias"]

    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)],
                                  known_path=_conhecidas(tmp_path, [_entrada(ocorrencia)]))

    alvo = report["alvos"]["arquivos"]
    assert report["status"] == "completo_sem_ocorrencia" and alvo["ocorrencias"] == []
    assert [o["arquivo"] for o in alvo["ocorrencias_conhecidas"]] == ["docs/a.md"]
    assert report["conhecidas"]["aplicadas"] == 1 and report["conhecidas"]["nao_encontradas"] == []
    assert report["resumo"]["arquivos"] == {"status": "completo_sem_ocorrencia", "ocorrencias": 0, "conhecidas": 1}


def test_l4e_ocorrencia_nova_continua_bloqueando(tmp_path):
    repo = _repo(tmp_path, {"docs/a.md": f"chave = \"{AWS_KEY}\"\n"})
    [ocorrencia] = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)])["alvos"]["arquivos"]["ocorrencias"]
    (repo / "docs" / "a.md").write_text(f"\nchave = \"{AWS_KEY}\"\n", encoding="utf-8")  # mudou de linha

    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)],
                                  known_path=_conhecidas(tmp_path, [_entrada(ocorrencia)]))

    assert report["status"] == "completo_com_ocorrencia"
    assert report["conhecidas"]["nao_encontradas"][0]["linha"] == ocorrencia["linha"]


@pytest.mark.parametrize(("entrada", "erro"), [
    ({"alvo": "arquivos", "arquivo": "a.md", "linha": 1, "regra": "valor_exato:DENODO_PASSWORD",
      "justificativa": "não"}, "conhecidas_regra_proibida"),
    ({"alvo": "arquivos", "arquivo": "a.md", "linha": 1, "regra": "cpf_valido", "justificativa": "não"},
     "conhecidas_regra_proibida"),
    ({"alvo": "arquivos", "arquivo": "a.md", "linha": 1, "regra": "detect-secrets:X", "justificativa": " "},
     "conhecidas_sem_justificativa"),
    ({"alvo": "outro", "arquivo": "a.md", "regra": "detect-secrets:X", "justificativa": "x"}, "conhecidas_formato"),
    ({"alvo": "historico", "arquivo": "a.md", "blob": "XYZ", "regra": "detect-secrets:X", "justificativa": "x"},
     "conhecidas_formato"),
])
def test_l4e_lista_invalida_torna_a_auditoria_incompleta(tmp_path, entrada, erro):
    repo = _repo(tmp_path, {"docs/b.md": "# ok\n"})

    report = security_audit.audit(repo, ("arquivos",), env_paths=[_env(tmp_path)],
                                  known_path=_conhecidas(tmp_path, [entrada]))

    assert report["status"] == "incompleto" and "lista_conhecidas_invalida" in report["motivos_incompleto"]
    assert report["conhecidas"]["erro"] == erro


def test_l4e_lista_duplicada_ou_ilegivel(tmp_path):
    entrada = {"alvo": "arquivos", "arquivo": "a.md", "linha": 1, "regra": "detect-secrets:X", "justificativa": "x"}
    with pytest.raises(security_audit.AuditError, match="conhecidas_duplicada"):
        security_audit.load_known(_conhecidas(tmp_path, [entrada, dict(entrada)]))
    ruim = tmp_path / "ruim.json"
    ruim.write_text("[]", encoding="utf-8")
    with pytest.raises(security_audit.AuditError, match="conhecidas_formato"):
        security_audit.load_known(ruim)


def test_l4e_lista_do_repositorio_e_valida_e_sem_regras_proibidas():
    entradas = security_audit.load_known(security_audit.KNOWN_FILE)
    assert entradas and not [e for e in entradas if e["regra"].startswith(security_audit.NEVER_KNOWN)]


def test_l4e_proibido_revisado_no_historico_nao_esconde_o_indice(tmp_path):
    repo = _repo(tmp_path, {"setup/configurar_env.ps1": "# placeholder\n", "lib/a.py": "A = 1\n"})
    _git(repo, "rm", "-q", "setup/configurar_env.ps1")  # sai do índice e do disco; fica no histórico
    _git(repo, "commit", "-q", "-m", "remove")
    entrada = {"alvo": "proibidos", "arquivo": "setup/configurar_env.ps1", "regra": "area_privada",
               "origem": ["historico"], "justificativa": "só placeholders; histórico mantido"}
    conhecidas = _conhecidas(tmp_path, [entrada])

    so_historico = security_audit.audit(repo, ("proibidos",), env_paths=[_env(tmp_path)], known_path=conhecidas)
    assert so_historico["status"] == "completo_sem_ocorrencia"

    (repo / "setup").mkdir(exist_ok=True)
    (repo / "setup" / "configurar_env.ps1").write_text("# placeholder\n", encoding="utf-8")
    _git(repo, "add", "-f", "setup/configurar_env.ps1")  # volta ao índice
    de_novo = security_audit.audit(repo, ("proibidos",), env_paths=[_env(tmp_path)], known_path=conhecidas)
    assert de_novo["status"] == "completo_com_ocorrencia"
    assert _rules(de_novo, "proibidos") == [("setup/configurar_env.ps1", "area_privada")]
