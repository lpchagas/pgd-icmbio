"""Ponte temporária: o módulo vive em relatorios/insights_engine.py desde o L4a.

Importar ocde.relatorios.insights_engine devolve o mesmo objeto de relatorios.insights_engine
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import insights_engine as _modulo

sys.modules[__name__] = _modulo
