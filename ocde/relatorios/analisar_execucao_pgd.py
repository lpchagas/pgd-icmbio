"""Ponte temporária: o módulo vive em relatorios/analisar_execucao_pgd.py desde o L4a.

Importar ocde.relatorios.analisar_execucao_pgd devolve o mesmo objeto de relatorios.analisar_execucao_pgd
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import analisar_execucao_pgd as _modulo

sys.modules[__name__] = _modulo
