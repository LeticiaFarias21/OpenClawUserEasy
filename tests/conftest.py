import sys
from unittest.mock import MagicMock

# Como o código do sistema tenta importar 'core.logger_config' mas o arquivo
# real está em 'utils/logger_config.py', mockamos para os testes passarem.
sys.modules['core.logger_config'] = MagicMock()
sys.modules['logger_config'] = MagicMock()
sys.modules['utils.logger_config'] = MagicMock()

# Mocks de bibliotecas pesadas e externas utilizadas em skills
sys.modules['chromadb'] = MagicMock()
sys.modules['fastembed'] = MagicMock()
