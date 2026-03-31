import os
import unittest
from unittest.mock import patch, mock_open
from core.agent_factory import create_openclaw_agent

class TestAgentFactory(unittest.TestCase):
    @patch('core.agent_factory.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('core.agent_factory.os.getenv')
    def test_create_openclaw_agent_success(self, mock_getenv, mock_file, mock_makedirs):
        # Configurar mock para o getenv retornar um modelo padrão caso model=None
        mock_getenv.return_value = "modelo_mockado:latest"

        # Parâmetros simulados
        name = "Agente Teste"
        role = "Papel de Teste"
        goal = "Objetivo de Teste"
        workflow_steps = ["Passo 1", "Passo 2"]

        # Chamar a função
        create_openclaw_agent(name, role, goal, workflow_steps)

        # Verificações
        mock_makedirs.assert_called_once_with("agentes", exist_ok=True)

        expected_filename = os.path.join("agentes", "Agente_Teste.md")
        mock_file.assert_called_once_with(expected_filename, 'w', encoding='utf-8')

        # Verifica se o conteúdo foi escrito (pega todos os writes chamados e junta)
        handle = mock_file()
        escrito = "".join(call.args[0] for call in handle.write.call_args_list)

        self.assertIn("# Identity: Agente Teste", escrito)
        self.assertIn("- **Role**: Papel de Teste", escrito)
        self.assertIn("- **Goal**: Objetivo de Teste", escrito)
        self.assertIn("- **Model**: modelo_mockado:latest", escrito)
        self.assertIn("1. Passo 1", escrito)
        self.assertIn("2. Passo 2", escrito)

    @patch('core.agent_factory.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_openclaw_agent_with_custom_model(self, mock_file, mock_makedirs):
        create_openclaw_agent("Nome", "Papel", "Meta", ["A"], model="qwen-custom")

        handle = mock_file()
        escrito = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertIn("- **Model**: qwen-custom", escrito)

if __name__ == '__main__':
    unittest.main()
