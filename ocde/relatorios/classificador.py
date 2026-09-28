"""Ponte temporária: o módulo vive em relatorios/classificador.py desde o L4a.

Importar ocde.relatorios.classificador devolve o mesmo objeto de relatorios.classificador
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import classificador as _modulo

sys.modules[__name__] = _modulo
