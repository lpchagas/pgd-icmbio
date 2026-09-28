"""Ponte temporária: o módulo vive em relatorios/textos_execucao.py desde o L4a.

Importar ocde.relatorios.textos_execucao devolve o mesmo objeto de relatorios.textos_execucao
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import textos_execucao as _modulo

sys.modules[__name__] = _modulo
