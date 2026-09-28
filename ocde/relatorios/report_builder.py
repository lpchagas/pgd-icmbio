"""Ponte temporária: o módulo vive em relatorios/report_builder.py desde o L4a.

Importar ocde.relatorios.report_builder devolve o mesmo objeto de relatorios.report_builder
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import report_builder as _modulo

sys.modules[__name__] = _modulo
