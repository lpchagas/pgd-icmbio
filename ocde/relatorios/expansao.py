"""Ponte temporária: o módulo vive em relatorios/expansao.py desde o L4a.

Importar ocde.relatorios.expansao devolve o mesmo objeto de relatorios.expansao
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import expansao as _modulo

sys.modules[__name__] = _modulo
