"""Ponte temporária: o módulo vive em relatorios/registros_execucao.py desde o L4a.

Importar ocde.relatorios.registros_execucao devolve o mesmo objeto de relatorios.registros_execucao
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import registros_execucao as _modulo

sys.modules[__name__] = _modulo
