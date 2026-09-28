"""Ponte temporária de CLI: o módulo vive em relatorios/relatorio_v2.py desde o L4a.

`python -m ocde.relatorios.relatorio_v2` executa relatorios.relatorio_v2.main(); importar
ocde.relatorios.relatorio_v2 devolve o mesmo objeto de relatorios.relatorio_v2. Retirada conforme o plano, §4.
"""
import sys

from relatorios import relatorio_v2 as _modulo

if __name__ == "__main__":
    raise SystemExit(_modulo.main())
sys.modules[__name__] = _modulo
