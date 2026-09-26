"""sitecustomize do replay de produção (tools/replay_producao.py).

Só age quando PGD_REPLAY_FIXTURES está definido, o que acontece apenas no
subprocesso aberto pelo replay. Substitui exclusivamente o I/O do A1:

- configuração e conexão Denodo (``get_config``, ``connect``), sem ler o .env;
- a conexão devolvida é um dublê JDBC (Statement/ResultSet) que serve as linhas
  congeladas de cada consulta; ``query_rows``/``clean`` reais continuam em uso;
- as planilhas de estrutura organizacional, trocadas pelas fixtures sintéticas.

Um audit hook recusa leitura de .env e do acervo privado, rede e subprocessos.
Ao sair, grava o registro com as consultas servidas e os módulos do projeto
carregados (com hash), usado pelo replay para comparar as dependências.
"""
from __future__ import annotations

import atexit
import hashlib
import json
import os
import re
import sys
from pathlib import Path

_PRIVADOS = ("artefatos_local", "cgov", "setup", "data")
_EVENTOS_PROIBIDOS = (
    "socket.connect",
    "socket.getaddrinfo",
    "subprocess.Popen",
    "os.system",
    "os.exec",
    "os.posix_spawn",
    "os.spawn",
    "os.startfile",
)
_DATAS = re.compile(r"CAST\('(\d{4}-\d{2}-\d{2})' AS DATE\)")


class ConsultaNaoCongelada(BaseException):
    """BaseException de propósito: o ``except Exception`` do A1 não a engole."""


def _sha256(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


def _instalar_bloqueios(raiz: str) -> None:
    privados = [os.path.join(raiz, nome) for nome in _PRIVADOS]

    def bloqueado(caminho: str) -> bool:
        absoluto = os.path.normcase(os.path.abspath(caminho))
        nome = os.path.basename(absoluto)
        if nome == ".env" or (nome.startswith(".env.") and nome != ".env.example"):
            return True
        return any(absoluto == p or absoluto.startswith(p + os.sep) for p in privados)

    def hook(evento: str, args: tuple) -> None:
        if evento == "open":
            alvo = args[0] if args else None
            if isinstance(alvo, bytes):
                alvo = os.fsdecode(alvo)
            if isinstance(alvo, (str, os.PathLike)) and bloqueado(os.fspath(alvo)):
                raise PermissionError("replay: leitura bloqueada de arquivo privado ou de ambiente")
        elif evento in _EVENTOS_PROIBIDOS:
            raise PermissionError(f"replay: {evento} bloqueado")

    sys.addaudithook(hook)


def _ativar() -> None:
    fixtures = Path(os.environ["PGD_REPLAY_FIXTURES"])
    raiz = os.path.normcase(os.path.abspath(os.environ["PGD_REPLAY_RAIZ"]))
    registro = Path(os.environ["PGD_REPLAY_REGISTRO"])

    variante = os.environ.get("PGD_REPLAY_VARIANTE", "")
    consultas = [
        item for item in json.loads((fixtures / "consultas.json").read_text(encoding="utf-8"))["consultas"]
        if not item.get("variantes") or variante in item["variantes"]
    ]
    servidas: list[dict] = []

    def localizar(chave: tuple, sql: str) -> dict | None:
        """Fixture cujo período e marcadores casam com a SQL.

        Período: as duas primeiras datas literais da SQL, ou (None, None) se não houver.
        Marcadores ``contem``/``nao_contem`` separam consultas do mesmo período (I08, G02).
        """

        candidatas = [
            item for item in consultas
            if chave == (item.get("inicio"), item.get("fim"))
            and all(trecho in sql for trecho in item.get("contem", ()))
            and not any(trecho in sql for trecho in item.get("nao_contem", ()))
        ]
        if len(candidatas) > 1:
            raise ConsultaNaoCongelada(f"fixtures ambíguas para o período {chave}")
        return candidatas[0] if candidatas else None

    def servir(sql: str) -> tuple[list[str], list[list]]:
        datas = _DATAS.findall(sql)[:2]
        chave = tuple(datas) if len(datas) == 2 else (None, None)
        item = localizar(chave, sql)
        servidas.append({
            "inicio": chave[0],
            "fim": chave[1],
            "nome": item.get("nome", "") if item else "",
            "sql_sha256": _sha256(sql.encode("utf-8")),
            "servida": item is not None,
        })
        if item is None:
            raise ConsultaNaoCongelada(f"sem linhas congeladas para a consulta do período {chave}")
        return list(item["colunas"]), [list(linha) for linha in item["linhas"]]

    # Traceback legível pelo replay (que decodifica UTF-8) também no console Windows.
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

    # Leituras das fixtures feitas acima; daqui em diante vale o bloqueio.
    _instalar_bloqueios(raiz)
    sys.modules["jpype"] = None  # qualquer tentativa de JVM real falha na importação

    import lib
    if not os.path.normcase(os.path.abspath(lib.__file__)).startswith(raiz + os.sep):
        raise RuntimeError("replay: pacote lib carregado fora da raiz sob teste")
    import lib.denodo_config as denodo_config
    import lib.estrutura_organizacional as estrutura
    import lib.monthly_runner as monthly_runner

    # Dublê no nível JDBC: o query_rows real (e o run_query próprio do G01) percorre
    # um ResultSet congelado, então clean() e a leitura de colunas continuam sob teste.
    class ResultadoCongelado:
        def __init__(self, colunas: list[str], linhas: list[list]) -> None:
            self._colunas, self._linhas, self._atual = colunas, linhas, -1

        def getMetaData(self):
            return self

        def getColumnCount(self) -> int:
            return len(self._colunas)

        def getColumnLabel(self, indice: int) -> str:
            return self._colunas[indice - 1]

        def next(self) -> bool:
            self._atual += 1
            return self._atual < len(self._linhas)

        def getObject(self, indice: int):
            return self._linhas[self._atual][indice - 1]

        def close(self) -> None:
            return None

    class ComandoCongelado:
        def executeQuery(self, sql: str) -> ResultadoCongelado:
            return ResultadoCongelado(*servir(sql))

        def close(self) -> None:
            return None

    class ConexaoCongelada:
        def createStatement(self) -> ComandoCongelado:
            return ComandoCongelado()

        def close(self) -> None:
            return None

    def get_config(require_credentials: bool = True):
        return denodo_config.DenodoConfig(
            host="replay.invalid", port="0", database="replay", user="replay",
            password="", driver_path=Path(), jvm_dll=Path(),
        )

    def connect(config):
        return ConexaoCongelada()

    for modulo in (denodo_config, monthly_runner):
        modulo.get_config = get_config
        modulo.connect = connect
    denodo_config.load_dotenv = lambda *args, **kwargs: None

    def planilha(nome: str) -> Path:
        propria = fixtures / nome
        return propria if propria.exists() else fixtures.parent / "_comum" / nome

    estrutura.DEFAULT_ESTRUTURA_CSV = planilha("ICMBIO_estrutura.csv")
    estrutura.DEFAULT_DICIONARIO_CSV = planilha("dicionario_petrvs_digiteca_v2.csv")

    def gravar_registro() -> None:
        proprio = os.path.normcase(os.path.abspath(__file__))
        modulos: dict[str, str] = {}
        for modulo in list(sys.modules.values()):
            arquivo = getattr(modulo, "__file__", None)
            if not arquivo:
                continue
            absoluto = os.path.normcase(os.path.abspath(arquivo))
            if absoluto != proprio and absoluto.startswith(raiz + os.sep):
                relativo = os.path.relpath(absoluto, raiz).replace(os.sep, "/")
                modulos[relativo] = _sha256(Path(arquivo).read_bytes())
        registro.write_text(
            json.dumps({"ativo": True, "consultas": servidas, "modulos": dict(sorted(modulos.items()))},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    atexit.register(gravar_registro)


if os.environ.get("PGD_REPLAY_FIXTURES"):
    _ativar()
