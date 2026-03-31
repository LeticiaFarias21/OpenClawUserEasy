import unittest
from unittest.mock import patch, MagicMock

# Ajuste de imports mockados globalmente no conftest.py para logger_config e fastembed, 
# então podemos importar com segurança
from main import preparar_agentes, executar_fluxo_juridico

class TestMain(unittest.TestCase):

    @patch('main.create_openclaw_agent')
    @patch('main.os.makedirs')
    def test_preparar_agentes(self, mock_makedirs, mock_create):
        preparar_agentes()
        
        # Verifica se o diretório de agentes é criado
        mock_makedirs.assert_called_once_with("agentes", exist_ok=True)
        # Verifica se as identidades são chamadas 2 vezes (triagem e analista)
        self.assertEqual(mock_create.call_count, 2)
        
        args_triagem = mock_create.call_args_list[0][1]
        self.assertEqual(args_triagem['name'], "Agente_Triagem")
        
        args_analista = mock_create.call_args_list[1][1]
        self.assertEqual(args_analista['name'], "Agente_Analista")

    @patch('main.buscar_jurisprudencia')
    @patch('main.OllamaAgent')
    def test_executar_fluxo_juridico(self, mock_ollama_agent_class, mock_buscar_juris):
        # Configurar mocks dos agentes instanciados
        mock_agente_triagem = MagicMock()
        mock_agente_analista = MagicMock()
        
        # O side_effect retorna os mocks na ordem em que são instanciados no executar_fluxo_juridico
        mock_ollama_agent_class.side_effect = [mock_agente_triagem, mock_agente_analista]
        
        # Configurar os retornos intermédiarios
        mock_agente_triagem.receive_message.return_value = "Resumo da Triagem."
        mock_buscar_juris.return_value = "Conforme Jurisprudência X."
        mock_agente_analista.receive_message.return_value = "Parecer Final Gerado."
        
        # Chamar a função principal
        resultado = executar_fluxo_juridico("Texto extraído da petição")
        
        # Asserts
        mock_agente_triagem.receive_message.assert_called_once_with("Texto extraído da petição", "Protocolo")
        mock_buscar_juris.assert_called_once_with("Resumo da Triagem.")
        
        esperado_prompt_analista = "DADOS DA PETIÇÃO: Resumo da Triagem.\n\nJURISPRUDÊNCIA ENCONTRADA: Conforme Jurisprudência X."
        mock_agente_analista.receive_message.assert_called_once_with(esperado_prompt_analista, "Agente_Triagem + NomicSearch")
        
        self.assertEqual(resultado, "Parecer Final Gerado.")

if __name__ == '__main__':
    unittest.main()
