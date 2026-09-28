"""Pontes temporárias para relatorios/ (L4a da reorganização).

Os módulos foram movidos para o pacote de nível superior ``relatorios``. Cada
``ocde/relatorios/<modulo>.py`` é uma ponte sem lógica que substitui a si mesma,
em ``sys.modules``, pelo módulo real: identidade, execução única e símbolos
privados preservados, sem ``import *`` e sem importar os demais módulos. As CLIs
(``relatorio_v2``, ``relatorio_cumulativo``) também repassam ``__main__``.

Retirada (plano, §4): ``privacidade`` e ``textos_execucao`` (importados pelos A1
certificados do G01/G02) só na próxima revisão metodológica; as demais após dois
ciclos mensais completos sem consumidor conhecido, registradas no CHANGELOG.
"""
