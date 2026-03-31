import sys
import unittest
from unittest.mock import patch, MagicMock

# Como TextEmbedding do FastEmbed é instanciado no nível do módulo (import),
# fazemos o mock antes de importar a função buscar_jurisprudencia
sys.modules['chromadb'] = MagicMock()
sys.modules['fastembed'] = MagicMock()

# Agora podemos importar testar
from skills.buscar_jurisprudencia import buscar_jurisprudencia, embedding_model, chromadb

class TestBuscarJurisprudencia(unittest.TestCase):

    def setUp(self):
        embedding_model.embed.reset_mock()

    @patch('skills.buscar_jurisprudencia.chromadb.PersistentClient')
    def test_buscar_jurisprudencia_success(self, mock_chroma_client):
        # Configurar retorno do embedding_model.embed
        # Ele retorna um gerador ou iterável que o código faz list()
        embedding_model.embed.return_value = [[0.1, 0.2, 0.3]]

        # Configurar mock cliente e collection
        mock_client_instance = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance

        # Configurar os resultados devolvidos pelo banco
        mock_collection.query.return_value = {
            "documents": [
                ["Sentença 1: Danos morais reconhecidos.", "Sentença 2: Valores atualizados."]
            ]
        }

        pergunta = "Qual a jurisprudência para danos morais?"
        resultado = buscar_jurisprudencia(pergunta)

        # Asserts
        embedding_model.embed.assert_called_once_with([pergunta])
        mock_chroma_client.assert_called_once()
        mock_client_instance.get_or_create_collection.assert_called_once_with(name="jurisprudencia_2026")
        
        # Verifica se collection.query foi devidamente chamada com o vetor esperado
        mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2, 0.3]], 
            n_results=3
        )

        expected_text = "Sentença 1: Danos morais reconhecidos.\n\n--- TRECHO RELEVANTE ---\nSentença 2: Valores atualizados."
        self.assertIn("Sentença 1", resultado)
        self.assertIn("TRECHO RELEVANTE", resultado)

    @patch('skills.buscar_jurisprudencia.chromadb.PersistentClient')
    def test_buscar_jurisprudencia_no_results(self, mock_chroma_client):
        embedding_model.embed.return_value = [[0.4, 0.5]]

        mock_client_instance = MagicMock()
        mock_collection = MagicMock()
        mock_client_instance.get_or_create_collection.return_value = mock_collection
        mock_chroma_client.return_value = mock_client_instance

        # Retornando banco vazio
        mock_collection.query.return_value = {
            "documents": [[]]
        }

        resultado = buscar_jurisprudencia("Teste sem resultados")
        
        self.assertEqual(resultado, "Nenhuma jurisprudência relevante encontrada para este caso.")

    def test_buscar_jurisprudencia_exception(self):
        # Testa o tratamento de exceção (por exemplo, quando o embed falhar ou chromadb falhar)
        # Forçamos uma exceção
        with patch('skills.buscar_jurisprudencia.chromadb.PersistentClient', side_effect=Exception("Erro Conexão")):
            resultado = buscar_jurisprudencia("Perguntando ao nada")
            
            self.assertIn("Erro técnico ao aceder à base", resultado)

if __name__ == '__main__':
    unittest.main()
