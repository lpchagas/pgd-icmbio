"""Ponte temporária: o módulo vive em relatorios/privacidade.py desde o L4a.

Importar ocde.relatorios.privacidade devolve o mesmo objeto de relatorios.privacidade
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import privacidade as _modulo

sys.modules[__name__] = _modulo
