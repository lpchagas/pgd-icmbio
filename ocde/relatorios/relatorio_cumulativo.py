"""Ponte temporária de CLI: o módulo vive em relatorios/relatorio_cumulativo.py desde o L4a.

`python -m ocde.relatorios.relatorio_cumulativo` executa relatorios.relatorio_cumulativo.main(); importar
ocde.relatorios.relatorio_cumulativo devolve o mesmo objeto de relatorios.relatorio_cumulativo. Retirada conforme o plano, §4.
"""
import sys

from relatorios import relatorio_cumulativo as _modulo

if __name__ == "__main__":
    raise SystemExit(_modulo.main())
sys.modules[__name__] = _modulo
