"""Dados sintéticos do REG_EXEC — nenhuma informação real de servidor.

Cinco servidores fictícios e três entregas fictícias, montados para exercitar
justamente os casos que a RN-04 precisa distinguir: ciclo avaliado, ciclo
enviado sem avaliação, ciclo não enviado, ciclo nunca aberto e mês fora da
vigência do plano de trabalho.
"""
from __future__ import annotations

from datetime import date

from lib.periodos import periods_pt_within, resolve_period

CORTE = date(2026, 8, 31)

EQUIPE = [
    "Ana Ficticia", "Bruno Ficticio", "Carla Ficticia",
    "Diego Ficticio", "Elisa Ficticia",
]


def spec_q2():
    return resolve_period("Q2-2026", familia="pe", analysis_end=CORTE)


def meses_q2():
    return periods_pt_within(spec_q2(), CORTE)


def entregas():
    return [
        dict(
            unidade_dona_sigla="CGOV", unidade_dona_nome="Coordenacao de Governanca",
            unidade_executora_sigla="CGOV", plano_numero="PE-Q2", plano_status="ATIVO",
            entrega_uuid="11111111-1111-4111-8111-111111111111",
            entrega_titulo="Cadeia de Valor revisada",
            entrega_meta_texto="(etapas concluidas / previstas) x 100",
            entrega_destinatario="ICMBio", meta_json='{"quantitativo": 1}',
            progresso_esperado=60, progresso_realizado=60,
            entrega_inicio="2026-01-01", entrega_fim="2026-08-31",
        ),
        dict(
            unidade_dona_sigla="CGOV", unidade_dona_nome="Coordenacao de Governanca",
            unidade_executora_sigla="CGOV", plano_numero="PE-Q2", plano_status="ATIVO",
            entrega_uuid="22222222-2222-4222-8222-222222222222",
            entrega_titulo="Matriz de riscos atualizada",
            entrega_meta_texto="", entrega_destinatario="Comite Gestor",
            meta_json='{"porcentagem": 100}',
            progresso_esperado=80, progresso_realizado=35,
            entrega_inicio="2026-05-01", entrega_fim="2026-07-31",
        ),
        # Sem meta pactuada e sem prazo: precisa aparecer, nunca sumir.
        dict(
            unidade_dona_sigla="CGOV", unidade_dona_nome="Coordenacao de Governanca",
            unidade_executora_sigla="CGOV", plano_numero="PE-Q2", plano_status="ATIVO",
            entrega_uuid="33333333-3333-4333-8333-333333333333",
            entrega_titulo="Trilha formativa elaborada",
            entrega_meta_texto="", entrega_destinatario="servidores", meta_json="",
            progresso_esperado=0, progresso_realizado=0,
            entrega_inicio="2026-05-01", entrega_fim="",
        ),
    ]


def planos_vigentes():
    planos = [
        dict(
            unidade_sigla="CGOV", unidade_nome="Coordenacao de Governanca",
            unidade_pai_sigla="CGGE", servidor_nome=nome, plano_numero=f"PT-{posicao}",
            plano_status="ATIVO", plano_inicio="2026-01-01", plano_fim="2026-12-31",
        )
        for posicao, nome in enumerate(EQUIPE, start=1)
    ]
    # Diego entrou em julho — maio e junho não são exigíveis dele.
    planos[3]["plano_inicio"] = "2026-07-01"
    return planos


def consolidacoes():
    registros = []
    for posicao, nome in enumerate(EQUIPE, start=1):
        for mes in meses_q2():
            if nome == "Diego Ficticio" and mes.rotulo in ("M05-2026", "M06-2026"):
                continue
            if nome == "Elisa Ficticia" and mes.rotulo == "M08-2026":
                continue  # ciclo nunca aberto
            status, avaliacao = "AVALIADO", "2026-07-05"
            if nome == "Bruno Ficticio" and mes.rotulo == "M07-2026":
                status, avaliacao = "CONCLUIDO", ""  # aguardando a chefia
            if nome == "Ana Ficticia" and mes.rotulo == "M08-2026":
                status, avaliacao = "INCLUIDO", ""  # servidor não enviou
            registros.append(dict(
                unidade_sigla="CGOV", servidor_nome=nome, plano_numero=f"PT-{posicao}",
                consolidacao_status=status, ciclo_inicio=mes.inicio.isoformat(),
                ciclo_fim=mes.fim.isoformat(), ciclo_conclusao="2026-07-02",
                ciclo_avaliacao=avaliacao, score_avaliacao="4",
                atividades_total="7", atividades_concluidas="6",
                horas_planejadas="120", horas_despendidas="118",
            ))
    return registros


def vinculos():
    return [
        dict(
            unidade_dona_sigla="CGOV", unidade_executora_sigla="CGOV",
            servidor_nome=nome, plano_entrega_numero="PE-Q2",
            entrega_uuid="11111111-1111-4111-8111-111111111111",
            plano_trabalho_numero=f"PT-{posicao}", plano_trabalho_status="ATIVO",
            forca_trabalho_perc="40", carga_horaria="40",
            forma_contagem_carga_horaria="HORAS",
            plano_inicio="2026-01-01", plano_fim="2026-12-31",
        )
        for posicao, nome in enumerate(EQUIPE[:3], start=1)
    ]
