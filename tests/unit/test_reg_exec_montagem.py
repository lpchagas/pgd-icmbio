"""Montagem das visões do REG_EXEC e renderização do registro de execução."""
import csv
import io
from datetime import date

import pytest

from gestao.reg_exec_montagem import (
    CICLOS_COLUNAS,
    PAINEL_COLUNAS,
    dias_de_sobreposicao,
    entrega_ref,
    montar_ciclos,
    montar_entregas,
    montar_painel,
    montar_vinculos,
    remover_colunas_pessoais,
)
from gestao.reg_exec_regras import servidor_refs
from gestao.reg_exec_relatorio import render_markdown
from lib.periodos import period_metadata
from ocde.relatorios.privacidade import forbidden_fields, scan_text
from ocde.relatorios.textos_execucao import TextSanitizer
from tests.fixtures import reg_exec_sintetico as dados

pytestmark = pytest.mark.unit


@pytest.fixture
def spec():
    return dados.spec_q2()


@pytest.fixture
def meses():
    return dados.meses_q2()


@pytest.fixture
def refs():
    return servidor_refs([p["servidor_nome"] for p in dados.planos_vigentes()])


@pytest.fixture
def visoes(spec, meses, refs):
    entregas = montar_entregas(dados.entregas(), spec)
    ciclos = montar_ciclos(dados.consolidacoes(), dados.planos_vigentes(), spec, meses, refs=refs)
    vinculos = montar_vinculos(dados.vinculos(), spec, refs=refs)
    painel = montar_painel(*entregas, *ciclos, spec)
    return entregas, ciclos, vinculos, painel


def linhas_como_dict(visao):
    colunas, linhas = visao
    return [dict(zip(colunas, linha)) for linha in linhas]


class TestPeriodo:
    def test_q2_e_quadrimestre_de_quatro_meses(self, spec, meses):
        assert (spec.inicio, spec.fim) == (date(2026, 5, 1), date(2026, 8, 31))
        assert spec.ciclo_tipo == "quadrimestral"
        assert [m.rotulo for m in meses] == [
            "M05-2026", "M06-2026", "M07-2026", "M08-2026"]

    def test_colunas_de_metadado_prefixam_todas_as_visoes(self, visoes):
        for colunas, _linhas in visoes:
            assert colunas[: len(period_metadata())] == period_metadata()


class TestEntregas:
    def test_uma_linha_por_entrega(self, visoes):
        assert len(linhas_como_dict(visoes[0])) == 3

    def test_entrega_sem_meta_aparece_e_nao_cumpre(self, visoes):
        registros = linhas_como_dict(visoes[0])
        sem_meta = [r for r in registros if r["meta_tipo"] == "N/D"]
        assert len(sem_meta) == 1
        assert sem_meta[0]["situacao"] == "nao_iniciada"

    def test_entrega_sem_prazo_e_sinalizada_nao_descartada(self, visoes):
        registros = linhas_como_dict(visoes[0])
        assert any(r["prazo_status"] == "sem_prazo_cadastrado" for r in registros)

    def test_semaforo_usa_o_fim_do_periodo_nao_a_data_de_hoje(self, visoes):
        # A entrega cumprida com prazo em 31/08 não pode disparar o gatilho de
        # prazo vencido; com date.today() (posterior) ela dispararia.
        registros = {r["entrega_titulo"]: r for r in linhas_como_dict(visoes[0])}
        cumprida = registros["Cadeia de Valor revisada"]
        assert "prazo_vencido_sem_conclusao" not in cumprida["gatilhos"]
        assert cumprida["semaforo"] == "🟢"
        atrasada = registros["Matriz de riscos atualizada"]
        assert "prazo_vencido_sem_conclusao" in atrasada["gatilhos"]
        assert atrasada["semaforo"] == "🔴"

    def test_pontuacao_zero_nao_vira_vazio(self, visoes):
        registros = linhas_como_dict(visoes[0])
        assert any(r["pontuacao_prioridade"] == "0" for r in registros)

    def test_referencia_da_entrega_e_estavel_e_nao_e_uuid(self):
        primeiro = entrega_ref("11111111-1111-4111-8111-111111111111")
        assert primeiro == entrega_ref("11111111-1111-4111-8111-111111111111")
        assert primeiro != entrega_ref("22222222-2222-4222-8222-222222222222")
        assert scan_text(f"cabecalho\n{primeiro}") == []
        assert entrega_ref("") == ""


class TestCiclosRN04:
    def test_matriz_cobre_todo_plano_vigente_em_todo_mes(self, visoes):
        assert len(linhas_como_dict(visoes[1])) == 5 * 4

    def test_mes_fora_da_vigencia_nao_conta_como_esperado(self, visoes):
        registros = linhas_como_dict(visoes[1])
        fora = [r for r in registros if r["rn04_situacao"] == "fora_da_vigencia"]
        assert len(fora) == 2  # Diego, admitido em julho
        assert all(r["rn04_bloqueio"] == "NAO" for r in fora)

    def test_cada_modo_de_bloqueio_aparece_uma_vez(self, visoes):
        situacoes = [r["rn04_situacao"] for r in linhas_como_dict(visoes[1])]
        assert situacoes.count("aguardando_avaliacao") == 1
        assert situacoes.count("nao_enviado") == 1
        assert situacoes.count("ciclo_nao_aberto") == 1

    def test_consolidacao_casada_por_sobreposicao(self, visoes):
        registros = linhas_como_dict(visoes[1])
        avaliados = [r for r in registros if r["rn04_situacao"] == "avaliado"]
        assert len(avaliados) == 15
        assert all(r["consolidacao_status"] == "AVALIADO" for r in avaliados)


class TestPainel:
    def test_agregados_e_veredito(self, visoes):
        painel = linhas_como_dict(visoes[3])
        assert len(painel) == 1
        linha = painel[0]
        assert linha["unidade_sigla"] == "CGOV"
        assert linha["entregas_no_periodo"] == "3"
        assert linha["entregas_com_meta"] == "2"
        assert linha["entregas_cumpridas"] == "1"
        assert linha["taxa_cumprimento_perc"] == "50.00"
        assert linha["ciclos_pt_esperados"] == "18"  # 20 menos os 2 fora da vigência
        assert linha["ciclos_pt_registrados"] == "17"
        assert linha["ciclos_pt_avaliados"] == "15"
        assert linha["ciclos_pt_pendentes"] == "3"
        assert linha["rn04_apto_conclusao"] == "NAO"

    def test_sem_pendencia_o_veredito_libera(self, spec, meses, refs):
        consolidacoes = [
            dict(registro, consolidacao_status="AVALIADO", ciclo_avaliacao="2026-07-05")
            for registro in dados.consolidacoes()
        ]
        # Reabre o ciclo que a fixture deixa inexistente.
        consolidacoes.append(dict(
            unidade_sigla="CGOV", servidor_nome="Elisa Ficticia", plano_numero="PT-5",
            consolidacao_status="AVALIADO", ciclo_inicio="2026-08-01",
            ciclo_fim="2026-08-31", ciclo_conclusao="2026-09-01",
            ciclo_avaliacao="2026-09-05", score_avaliacao="4",
            atividades_total="5", atividades_concluidas="5",
            horas_planejadas="120", horas_despendidas="120",
        ))
        entregas = montar_entregas(dados.entregas(), spec)
        ciclos = montar_ciclos(consolidacoes, dados.planos_vigentes(), spec, meses, refs=refs)
        painel = linhas_como_dict(montar_painel(*entregas, *ciclos, spec))
        assert painel[0]["ciclos_pt_pendentes"] == "0"
        assert painel[0]["rn04_apto_conclusao"] == "SIM"

    def test_colunas_do_painel_sao_o_contrato_publicado(self, visoes):
        colunas, _linhas = visoes[3]
        assert colunas == list(period_metadata()) + list(PAINEL_COLUNAS)


class TestSobreposicao:
    def test_plano_anual_recortado_no_quadrimestre(self, spec):
        assert dias_de_sobreposicao(date(2026, 1, 1), date(2026, 12, 31), spec) == (123.0, 365.0)

    def test_plano_inteiramente_fora(self, spec):
        assert dias_de_sobreposicao(date(2025, 1, 1), date(2025, 3, 1), spec) == (0.0, 60.0)

    def test_datas_ausentes(self, spec):
        assert dias_de_sobreposicao(None, date(2026, 8, 31), spec) == (None, None)


class TestPrivacidade:
    def test_produto_restrito_remove_nomes_de_todas_as_visoes(self, spec, meses, refs):
        ciclos = remover_colunas_pessoais(
            *montar_ciclos(dados.consolidacoes(), dados.planos_vigentes(), spec, meses, refs=refs))
        vinculos = remover_colunas_pessoais(*montar_vinculos(dados.vinculos(), spec, refs=refs))
        for colunas, linhas in (ciclos, vinculos):
            assert "servidor_nome" not in colunas
            texto = "\n".join("|".join(linha) for linha in linhas)
            assert not any(nome in texto for nome in dados.EQUIPE)

    def test_nenhuma_visao_usa_coluna_proibida(self, visoes):
        for colunas, _linhas in visoes:
            assert forbidden_fields(colunas) == []

    def test_csv_restrito_passa_na_varredura(self, spec, meses, refs):
        entregas = montar_entregas(dados.entregas(), spec, sanitizer=TextSanitizer(dados.EQUIPE))
        ciclos = remover_colunas_pessoais(
            *montar_ciclos(dados.consolidacoes(), dados.planos_vigentes(), spec, meses, refs=refs))
        for colunas, linhas in (entregas, ciclos):
            buffer = io.StringIO()
            escritor = csv.writer(buffer, delimiter="|")
            escritor.writerow(colunas)
            escritor.writerows(linhas)
            assert scan_text(buffer.getvalue()) == []

    def test_produto_operacional_preserva_os_nomes(self, visoes):
        colunas, _linhas = visoes[1]
        assert "servidor_nome" in colunas
        assert "servidor_nome" in CICLOS_COLUNAS


class TestRelatorio:
    def _render(self, spec, visoes, produto):
        entregas, ciclos, vinculos, painel = visoes
        if produto != "operacional":
            ciclos = remover_colunas_pessoais(*ciclos)
            vinculos = remover_colunas_pessoais(*vinculos)
        return render_markdown(
            spec=spec, escopo="CGOV", produto=produto, emitido_em=date(2026, 9, 14),
            entregas=entregas, ciclos=ciclos, vinculos=vinculos, painel=painel,
        )

    def test_secoes_obrigatorias_presentes(self, spec, visoes):
        markdown = self._render(spec, visoes, "operacional")
        for titulo in (
            "## 1. Resumo da execução das entregas",
            "## 2. Checagem de risco por entrega",
            "## 3. Verificação RN-04",
            "## 4. Força de trabalho declarada por entrega",
            "## 5. Painel consolidado por unidade",
            "## 6. Instruções para atualização no PETRVS",
            "## 7. Ressalvas metodológicas",
        ):
            assert titulo in markdown

    def test_matriz_tem_uma_coluna_por_mes(self, spec, visoes):
        markdown = self._render(spec, visoes, "operacional")
        cabecalho = [l for l in markdown.splitlines() if l.startswith("| Servidor | PT |")][0]
        assert cabecalho.count("M0") == 4

    def test_veredito_bloqueia_com_pendencia(self, spec, visoes):
        markdown = self._render(spec, visoes, "operacional")
        assert "NÃO pode ser concluído" in markdown
        assert "### 3.1 Bloqueios para a conclusão" in markdown

    def test_relatorio_restrito_nao_nomeia_servidor(self, spec, visoes):
        markdown = self._render(spec, visoes, "restrito")
        assert not any(nome in markdown for nome in dados.EQUIPE)
        assert "SERVIDOR_01" in markdown
        assert scan_text(markdown) == []

    def test_relatorio_operacional_nomeia_servidor(self, spec, visoes):
        markdown = self._render(spec, visoes, "operacional")
        assert "Ana Ficticia" in markdown

    def test_rotulo_q_e_tratado_como_quadrimestre(self, spec, visoes):
        markdown = self._render(spec, visoes, "operacional")
        assert "Q2-2026 (quadrimestre)" in markdown
        # A palavra "trimestre" só pode aparecer na ressalva que explica a
        # divergência herdada das planilhas — nunca descrevendo o período.
        antes_das_ressalvas = markdown.split("## 7. Ressalvas")[0]
        assert "trimestr" not in antes_das_ressalvas.lower()

    def test_ressalva_registra_o_conflito_de_calendario(self, spec, visoes):
        markdown = self._render(spec, visoes, "operacional")
        assert "C-01" in markdown and "01/05–30/07" in markdown

    def test_periodo_parcial_recebe_aviso(self, visoes):
        from lib.periodos import resolve_period
        parcial = resolve_period("Q3-2026", familia="pe", analysis_end=date(2026, 10, 31))
        markdown = render_markdown(
            spec=parcial, escopo="CGOV", produto="restrito", emitido_em=date(2026, 11, 1),
            entregas=visoes[0], ciclos=remover_colunas_pessoais(*visoes[1]),
            vinculos=remover_colunas_pessoais(*visoes[2]), painel=visoes[3],
        )
        assert "ainda **não encerrou**" in markdown
