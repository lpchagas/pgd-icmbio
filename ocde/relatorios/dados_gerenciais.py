"""Ponte temporária: o módulo vive em relatorios/dados_gerenciais.py desde o L4a.

Importar ocde.relatorios.dados_gerenciais devolve o mesmo objeto de relatorios.dados_gerenciais
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import dados_gerenciais as _modulo

sys.modules[__name__] = _modulo
