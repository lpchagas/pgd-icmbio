"""Ponte temporária: o módulo vive em relatorios/pdf_export.py desde o L4a.

Importar ocde.relatorios.pdf_export devolve o mesmo objeto de relatorios.pdf_export
(execução única, símbolos privados acessíveis). Retirada conforme o plano, §4.
"""
import sys

from relatorios import pdf_export as _modulo

sys.modules[__name__] = _modulo
