"""Regressão estática dos 12 scripts A1 (ocde/indicadores/IND_OCDE_XX.1_run.py).

Não executa nenhum script — lê o texto-fonte e aplica asserções regex.
Cada caso aqui corresponde a um bug histórico real, documentado em
CLAUDE.md §11 ("Bugs históricos corrigidos — não repetir"), que já
aconteceu neste projeto e foi corrigido silenciosamente uma vez.

IMPORTANTE: as asserções positivas (padrão correto presente) são checadas
dentro da string SQL_IXX/SQL_I01_PLANOS extraída do arquivo — nunca no
texto completo do módulo. As docstrings destes scripts documentam de
propósito o bug antigo (ex.: "o SQL original usava JSON_UNQUOTE..."), então
uma checagem ingênua de "JSON_UNQUOTE not in source" sobre o arquivo inteiro
daria falso positivo (falharia mesmo com o bug corrigido, por causa do
comentário histórico). Checar só dentro da SQL real evita essa armadilha.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.regression

INDICADORES_DIR = Path(__file__).resolve().parents[2] / "ocde" / "indicadores"

TODOS_OS_INDICADORES = [f"{i:02d}" for i in range(1, 13)]


def _source(indicador: str) -> str:
    path = INDICADORES_DIR / f"IND_OCDE_{indicador}.1_run.py"
    assert path.exists(), f"Script A1 não encontrado: {path}"
    return path.read_text(encoding="utf-8")


def _sql_constant(source: str, var_name: str) -> str:
    """Extrai o conteúdo de `VAR_NAME = \"\"\"...\"\"\"` — ignora docstrings/comentários."""
    match = re.search(rf'{re.escape(var_name)}\s*=\s*"""(.*?)"""', source, flags=re.DOTALL)
    assert match, f"Não encontrei a constante {var_name} no script."
    return match.group(1)


# ---------------------------------------------------------------------------
# Regressão: escala do Eixo 4 invertida (bug corrigido 12.06.2026 / 19.06.2026)
# JSON_UNQUOTE(tan.nota) não funciona no Denodo VQL e retornava NULL para
# todos os registros; sequencia=2/5 eram trocados com sequencia=4/1.
# ---------------------------------------------------------------------------

class TestEscalaEixo4:
    @pytest.mark.parametrize("indicador,var_name", [("09", "SQL_I09"), ("10", "SQL_I10"), ("11", "SQL_I11"), ("12", "SQL_I12")])
    def test_exporta_cobertura_distinta_de_servidores_avaliados(self, indicador, var_name):
        sql = _sql_constant(_source(indicador), var_name)
        assert re.search(
            r"COUNT\(DISTINCT\s+(?:avpt\.)?id_servidor\)\s+AS\s+total_servidores_avaliados",
            sql,
            flags=re.IGNORECASE,
        )

    @pytest.mark.parametrize("indicador,colunas", [
        ("09", ("media_nota_pt", "total_avaliacoes_pt")),
        ("10", ("perc_inadequado", "total_avaliacoes_pt")),
        ("11", ("perc_excepcional", "nivel_reconhecimento")),
        ("12", ("diferenca_absoluta", "classificacao_coerencia")),
    ])
    def test_diagnostico_localiza_colunas_por_nome(self, indicador, colunas):
        """Os avisos pós-CSV devem achar a coluna pelo nome, nunca por offset fixo.

        Offsets do tipo ``n + 5`` já quebraram duas vezes: com a inserção da
        coluna mesogrupo (05.08.2026) e com media_nota_pt_eventos (D11). A busca
        por nome é imune à inserção de colunas.
        """
        source = _source(indicador)
        for coluna in colunas:
            assert f'cols.index("{coluna}")' in source, (
                f"I{indicador} deve localizar {coluna} por nome."
            )
        assert not re.search(r"offset_\w+\s*=\s*n\s*\+\s*\d", source), (
            f"I{indicador} não pode voltar a usar offset posicional fixo."
        )

    @pytest.mark.parametrize("indicador", TODOS_OS_INDICADORES)
    def test_nenhum_a1_usa_offset_posicional_fixo(self, indicador):
        source = _source(indicador)
        assert not re.search(r"len\(meta_cols\)\s*\+\s*\d", source), (
            f"I{indicador} deve localizar colunas por nome, não por len(meta_cols) + N."
        )

    @pytest.mark.parametrize("indicador,var_name", [("09", "SQL_I09"), ("10", "SQL_I10"), ("11", "SQL_I11"), ("12", "SQL_I12")])
    def test_avaliacao_usa_data_de_negocio(self, indicador, var_name):
        sql = _sql_constant(_source(indicador), var_name)
        ocorrencias = len(re.findall(
            r"CAST\(av\.data_avaliacao AS DATE\)\s+BETWEEN\s+p\.data_inicio\s+AND\s+p\.data_fim",
            sql,
        ))
        esperado = 2 if indicador == "12" else 1
        assert ocorrencias == esperado

    @pytest.mark.parametrize("indicador,var_name", [("09", "SQL_I09"), ("12", "SQL_I12")])
    def test_score_usa_formula_correta(self, indicador, var_name):
        sql = _sql_constant(_source(indicador), var_name)
        assert re.search(r"\(\s*6\s*-\s*tan\.sequencia\s*\)", sql), (
            f"SQL_{var_name} deve calcular o score via (6 - tan.sequencia)."
        )
        assert "JSON_UNQUOTE" not in sql, (
            f"SQL_{var_name} não deve usar JSON_UNQUOTE (não suportado no Denodo VQL)."
        )

    def test_i10_inadequado_usa_sequencia_4(self):
        sql = _sql_constant(_source("10"), "SQL_I10")
        # aceita tan.sequencia = 4 diretamente ou via alias (ex.: sequencia_nota = 4)
        assert re.search(r"sequencia\w*\s*=\s*4", sql), (
            "I10 (Inadequado) deve filtrar por sequencia (ou alias) = 4."
        )
        assert "JSON_UNQUOTE" not in sql

    def test_i11_excepcional_usa_sequencia_1(self):
        sql = _sql_constant(_source("11"), "SQL_I11")
        assert re.search(r"sequencia\w*\s*=\s*1", sql), (
            "I11 (Excepcional) deve filtrar por sequencia (ou alias) = 1."
        )
        assert "JSON_UNQUOTE" not in sql


# ---------------------------------------------------------------------------
# Regressão: unidade errada em I07/I08 (bug corrigido — pt.unidade_id era o
# servidor, não o dono da entrega; correto é COALESCE(pe.unidade_id, ph.unidade_id))
# ---------------------------------------------------------------------------

class TestUnidadeI07I08:
    @pytest.mark.parametrize("indicador,var_name", [("07", "SQL_I07"), ("08", "SQL_I08")])
    def test_join_de_unidade_usa_o_dono_da_entrega(self, indicador, var_name):
        """A unidade é a dona do PE, nunca a do executor do PT.

        O fallback muda de nome conforme o script: I08 ainda tem o CTE
        planos_horas (``ph``), enquanto o I07 passou a ler ``pt`` diretamente
        depois que o rateio migrou para Python (decisão CGOV D09).
        """
        sql = _sql_constant(_source(indicador), var_name)
        assert re.search(
            r"COALESCE\(\s*pe\.unidade_id\s*,\s*(?:ph|pt)\.unidade_id\s*\)", sql
        ), f"{var_name} deve atribuir a unidade via COALESCE(pe.unidade_id, ...)."
        assert not re.search(r"un\.id\s*=\s*pt\.unidade_id\b", sql), (
            f"{var_name} não pode atribuir a entrega à unidade do executor."
        )

    @pytest.mark.parametrize("indicador,var_name", [("07", "SQL_I07"), ("08", "SQL_I08")])
    def test_rateio_de_horas_usa_dias_uteis(self, indicador, var_name):
        """D09: o rateio saiu da SQL e usa o calendário institucional."""
        source = _source(indicador)
        sql = _sql_constant(source, var_name)
        # A SQL devolve as datas brutas; quem divide é o Python.
        assert "AS sobreposicao_inicio" in sql and "AS sobreposicao_fim" in sql
        assert "from lib.calendario import dias_uteis" in source
        assert "dias_uteis(sobre_ini, sobre_fim)" in source
        assert "dias_uteis(inicio, fim)" in source

    def test_i08_emite_as_duas_perspectivas(self):
        """D10: numerador e denominador sempre da mesma unidade."""
        source = _source("08")
        sql = _sql_constant(source, "SQL_I08")
        assert "AS unidade_dona_sigla" in sql and "AS unidade_executora_sigla" in sql
        # Denominador vem de consulta própria: a capacidade inclui PTs sem
        # entrega vinculada, que não aparecem no universo de vínculos.
        assert "SQL_I08_CAPACIDADE" in source
        for coluna in ("proporcao_horas_perc", "proporcao_executora_perc",
                       "horas_executora", "capacidade_executora"):
            assert coluna in source, f"I08 deve exportar {coluna}."

    def test_i07_conta_planos_de_trabalho_nao_pessoas(self):
        """D09: num_servidores_alocados era um nome errado para o COUNT DISTINCT."""
        source = _source("07")
        assert "num_planos_trabalho_alocados" in source
        # O nome antigo só pode sobreviver na docstring que registra a mudança,
        # nunca como coluna de saída.
        assert '"num_servidores_alocados"' not in source


# ---------------------------------------------------------------------------
# Conformidade com o padrão canônico — comum aos 12 scripts A1
# (formaliza a Dimensão 1/2 de .claude/skills/p3b-auditar/SKILL.md)
# ---------------------------------------------------------------------------

class TestPadraoCanonico:
    @pytest.mark.parametrize("indicador", TODOS_OS_INDICADORES)
    def test_credenciais_vem_do_env_nunca_hardcoded(self, indicador):
        source = _source(indicador)
        assert "get_config(require_credentials=True)" in source or "get_config(" in source
        # nenhuma credencial literal deve aparecer nos scripts públicos
        assert not re.search(r'PASS\w*\s*=\s*["\'][^"\']{4,}["\']', source)
        assert not re.search(r"\b\d{11}\b", source), "CPF literal não deve aparecer no A1."

    @pytest.mark.parametrize("indicador", TODOS_OS_INDICADORES)
    def test_usa_write_pipe_csv_do_lib(self, indicador):
        source = _source(indicador)
        assert "from lib.csv_utils import" in source
        assert "write_pipe_csv" in source

    @pytest.mark.parametrize("indicador", TODOS_OS_INDICADORES)
    def test_usa_build_periods_pe_ou_pt(self, indicador):
        source = _source(indicador)
        assert "build_periods_pe" in source or "build_periods_pt" in source, (
            "Todo A1 deve usar a segmentação canônica de períodos de lib.periodos."
        )

    @pytest.mark.parametrize("indicador", TODOS_OS_INDICADORES)
    def test_injeta_analysis_end_explicitamente(self, indicador):
        source = _source(indicador)
        assert "window = analysis_window()" in source
        assert re.search(r"build_periods_(?:pe|pt)\(window\.fim\)", source), (
            "Todo A1 deve passar analysis_end explicitamente à segmentação canônica."
        )
        assert "date.today()" not in source

    @pytest.mark.parametrize("indicador", ["07", "08", "09", "10", "11", "12"])
    def test_aviso_de_ciclo_parcial_usa_novo_offset_e_status(self, indicador):
        """O status do ciclo vem da coluna periodo_status, localizada pelo nome."""
        source = _source(indicador)
        assert 'cols.index("periodo_status")' in source
        assert "\"parcial_no_corte\"" in source
        assert "r[4] == \"em_andamento\"" not in source
        assert "r[4] == \"encerrado\"" not in source

    @pytest.mark.parametrize("indicador", [i for i in TODOS_OS_INDICADORES if i != "01"])
    def test_conexao_e_fechada_no_finally(self, indicador):
        """I01 é a exceção documentada (query única + agregação em Python)."""
        source = _source(indicador)
        assert "conn.close()" in source, f"IND_OCDE_{indicador}.1_run.py deve fechar a conexão JDBC."

    @pytest.mark.parametrize("indicador", [i for i in TODOS_OS_INDICADORES if i != "01"])
    def test_loop_de_periodos_tem_try_except(self, indicador):
        """Falha de uma query em um período não deve abortar os demais períodos."""
        source = _source(indicador)
        assert "try:" in source and "except" in source, (
            f"IND_OCDE_{indicador}.1_run.py deve isolar erros por período com try/except."
        )
