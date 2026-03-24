import unittest
from unittest.mock import patch, MagicMock
from core.ollamaAgent import OllamaAgent

class TestSistemaJuridico(unittest.TestCase):

    def setUp(self):
        self.agent = OllamaAgent("TestAgent", "Analista", model="qwen3.5:0.8b")

    @patch('requests.post')
    def test_ask_ollama_success(self, mock_post):
        # Simula resposta de sucesso do Ollama
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'message': {'content': 'Resposta mockada'}
        }
        mock_post.return_value = mock_response

        res = self.agent.ask_ollama("Olá")
        self.assertEqual(res, "Resposta mockada")
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_ask_ollama_failure(self, mock_post):
        # Simula falha de conexão
        mock_post.side_effect = Exception("Connection Error")
        
        res = self.agent.ask_ollama("Olá")
        self.assertIn("Erro na comunicação", res)

    def test_agent_initialization(self):
        self.assertEqual(self.agent.name, "TestAgent")
        self.assertEqual(self.agent.model, "qwen3.5:0.8b")

if __name__ == '__main__':
    unittest.main()