"""Regras determinísticas do REG_EXEC — meta, desvio, RN-04 e capacidade."""
from datetime import date

import pytest

from gestao.reg_exec_regras import (
    SEMAFORO_ALERTA,
    SEMAFORO_ATENCAO,
    SEMAFORO_NAO_APLICA,
    SEMAFORO_OK,
    anomalia_escala,
    ciclo_dentro_da_vigencia,
    desvio_pp,
    entrega_cumprida,
    horas_contratuais,
    parse_meta,
    prazo_status,
    rn04_situacao,
    semaforo_de_prioridade,
    servidor_refs,
    situacao_entrega,
    taxa_meta_integral,
    to_date,
    to_number,
)

pytestmark = pytest.mark.unit


class TestMeta:
    @pytest.mark.parametrize("bruto,esperado", [
        ('{"quantitativo": 10}', (10.0, "quantitativo")),
        ('{"porcentagem": 100.0}', (100.0, "porcentagem")),
        ({"quantitativo": 3}, (3.0, "quantitativo")),
    ])
    def test_formatos_reconhecidos(self, bruto, esperado):
        assert parse_meta(bruto) == esperado

    @pytest.mark.parametrize("bruto", ["", None, "{", "[]", '{"outra": 1}'])
    def test_meta_ilegivel_nunca_levanta(self, bruto):
        assert parse_meta(bruto) == (None, "N/D")

    def test_denominador_zero_devolve_none(self):
        assert taxa_meta_integral(0, 5) is None
        assert taxa_meta_integral(None, 5) is None

    def test_taxa_arredondada(self):
        assert taxa_meta_integral(10, 7) == 70.0


class TestCumprimento:
    def test_sem_meta_pactuada_nunca_conta_como_cumprida(self):
        # Espelha ocde/relatorios/registros_execucao.py: progresso esperado
        # zero significa meta não pactuada, não meta trivialmente atingida.
        assert entrega_cumprida(0, 100) is False

    def test_realizado_igual_ao_esperado_cumpre(self):
        assert entrega_cumprida(80, 80) is True

    def test_superexecucao_preservada(self):
        assert entrega_cumprida(80, 120) is True
        assert desvio_pp(80, 120) == 40.0

    def test_desvio_preserva_sinal(self):
        assert desvio_pp(80, 60) == -20.0
        assert desvio_pp(None, 60) is None


class TestPrazoESituacao:
    def test_prazo_sem_cadastro_e_explicito(self):
        assert prazo_status(None, date(2026, 8, 31)) == "sem_prazo_cadastrado"

    @pytest.mark.parametrize("fim,esperado", [
        (date(2026, 7, 31), "vencido"),
        (date(2026, 8, 31), "vence_na_referencia"),
        (date(2026, 9, 30), "vigente"),
    ])
    def test_prazo(self, fim, esperado):
        assert prazo_status(fim, date(2026, 8, 31)) == esperado

    def test_concluida_apos_o_prazo_recebe_ressalva(self):
        assert situacao_entrega("ATIVO", 80, 80, "vencido") == "concluida_com_ressalva"

    def test_cancelada_e_suspensa_prevalecem(self):
        assert situacao_entrega("CANCELADO", 80, 80, "vigente") == "cancelada"
        assert situacao_entrega("SUSPENSO", 10, 5, "vigente") == "suspensa"

    def test_sem_progresso_e_nao_iniciada(self):
        assert situacao_entrega("ATIVO", 50, 0, "vigente") == "nao_iniciada"


class TestAnomaliaEscala:
    def test_valores_negativos_sinalizados(self):
        assert "progresso_esperado_negativo" in anomalia_escala(-1, 10, "quantitativo")
        assert "meta_negativa" in anomalia_escala(10, -5, "quantitativo")

    def test_percentual_acima_de_cem(self):
        assert "meta_percentual_acima_de_100" in anomalia_escala(50, 150, "porcentagem")

    def test_escalas_divergentes(self):
        assert "escalas_divergentes_0a1_vs_0a100" in anomalia_escala(60, 0.6, "porcentagem")

    def test_caso_normal_sem_anomalia(self):
        assert anomalia_escala(60, 100, "porcentagem") == ""


class TestRN04:
    def test_avaliado_libera(self):
        resultado = rn04_situacao("AVALIADO", False, True)
        assert (resultado.situacao, resultado.semaforo, resultado.bloqueia) == (
            "avaliado", SEMAFORO_OK, False)

    def test_concluido_ainda_bloqueia(self):
        # CONCLUIDO no PETRVS significa "enviado, aguardando avaliação da
        # chefia" — tratá-lo como resolvido é o erro silencioso do produto.
        resultado = rn04_situacao("CONCLUIDO", False, True)
        assert resultado.situacao == "aguardando_avaliacao"
        assert resultado.semaforo == SEMAFORO_ATENCAO
        assert resultado.bloqueia is True

    def test_incluido_bloqueia(self):
        resultado = rn04_situacao("INCLUIDO", False, True)
        assert resultado.situacao == "nao_enviado"
        assert resultado.semaforo == SEMAFORO_ALERTA
        assert resultado.bloqueia is True

    def test_ciclo_nunca_aberto_bloqueia(self):
        resultado = rn04_situacao("", False, True)
        assert resultado.situacao == "ciclo_nao_aberto"
        assert resultado.bloqueia is True

    def test_fora_da_vigencia_nao_bloqueia_nem_conta(self):
        resultado = rn04_situacao("", False, False)
        assert resultado.situacao == "fora_da_vigencia"
        assert resultado.semaforo == SEMAFORO_NAO_APLICA
        assert resultado.bloqueia is False
        assert resultado.conta_como_esperado is False

    def test_status_desconhecido_bloqueia_por_precaucao(self):
        resultado = rn04_situacao("ARQUIVADO", False, True)
        assert resultado.bloqueia is True
        assert "nao_previsto" in resultado.situacao

    def test_avaliacao_registrada_prevalece_sobre_status(self):
        assert rn04_situacao("CONCLUIDO", True, True).situacao == "avaliado"


class TestVigencia:
    def test_admissao_no_meio_do_quadrimestre(self):
        # Plano iniciado em julho: maio não é exigível.
        assert ciclo_dentro_da_vigencia(
            date(2026, 5, 1), date(2026, 5, 31), date(2026, 7, 1), date(2026, 12, 31)
        ) is False
        assert ciclo_dentro_da_vigencia(
            date(2026, 7, 1), date(2026, 7, 31), date(2026, 7, 1), date(2026, 12, 31)
        ) is True

    def test_exoneracao_encerra_exigencia(self):
        assert ciclo_dentro_da_vigencia(
            date(2026, 8, 1), date(2026, 8, 31), date(2026, 1, 1), date(2026, 6, 30)
        ) is False

    def test_datas_ausentes_mantem_exigencia(self):
        assert ciclo_dentro_da_vigencia(
            date(2026, 5, 1), date(2026, 5, 31), None, None
        ) is True


class TestCapacidade:
    def test_forma_em_dias_multiplica_por_oito(self):
        assert horas_contratuais(5, "DIAS", 10, 10, 100) == 40.0
        assert horas_contratuais(40, "HORAS", 10, 10, 100) == 40.0

    def test_proporcional_a_sobreposicao_e_a_forca(self):
        assert horas_contratuais(40, "HORAS", 5, 10, 50) == 10.0

    def test_denominador_zero_devolve_none(self):
        assert horas_contratuais(40, "HORAS", 5, 0, 50) is None
        assert horas_contratuais(None, "HORAS", 5, 10, 50) is None


class TestAuxiliares:
    def test_pseudonimos_deterministicos_e_ordenados(self):
        assert servidor_refs(["Carla", "Ana", "Bruno", "Ana"]) == {
            "Ana": "SERVIDOR_01", "Bruno": "SERVIDOR_02", "Carla": "SERVIDOR_03"}

    def test_pseudonimo_ignora_vazios(self):
        assert servidor_refs(["", "  ", "Ana"]) == {"Ana": "SERVIDOR_01"}

    def test_semaforo_por_prioridade(self):
        assert semaforo_de_prioridade("crítica") == SEMAFORO_ALERTA
        assert semaforo_de_prioridade("alta") == SEMAFORO_ALERTA
        assert semaforo_de_prioridade("moderada") == SEMAFORO_ATENCAO
        assert semaforo_de_prioridade("rotina") == SEMAFORO_OK

    def test_conversoes_tolerantes(self):
        assert to_number("12,5") == 12.5
        assert to_number("", 0.0) == 0.0
        assert to_number("abc") is None
        assert to_date("2026-05-01T10:00:00") == date(2026, 5, 1)
        assert to_date("") is None
