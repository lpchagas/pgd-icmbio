"""Ponte temporária: o módulo vive em relatorios/loader.py desde o L4a.

Importar ocde.relatorios.loader devolve o mesmo objeto de relatorios.loader
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import loader as _modulo

sys.modules[__name__] = _modulo
