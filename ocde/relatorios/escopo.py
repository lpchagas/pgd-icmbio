"""Ponte temporária: o módulo vive em relatorios/escopo.py desde o L4a.

Importar ocde.relatorios.escopo devolve o mesmo objeto de relatorios.escopo
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import escopo as _modulo

sys.modules[__name__] = _modulo
