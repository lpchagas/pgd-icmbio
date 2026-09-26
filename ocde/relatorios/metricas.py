"""Ponte temporária: o módulo vive em relatorios/metricas.py desde o L4a.

Importar ocde.relatorios.metricas devolve o mesmo objeto de relatorios.metricas
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import metricas as _modulo

sys.modules[__name__] = _modulo
