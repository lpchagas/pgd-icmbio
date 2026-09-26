"""Ponte temporária: o módulo vive em relatorios/gestao_report.py desde o L4a.

Importar ocde.relatorios.gestao_report devolve o mesmo objeto de relatorios.gestao_report
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import gestao_report as _modulo

sys.modules[__name__] = _modulo
