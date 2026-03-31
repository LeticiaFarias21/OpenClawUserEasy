import unittest
from unittest.mock import patch, MagicMock
from skills.extract_peticao import extrair_elementos_peticao

class TestExtractPeticao(unittest.TestCase):

    @patch('skills.extract_peticao.fitz.open')
    def test_extrair_elementos_peticao_success(self, mock_fitz_open):
        # Criação dos mocks para simular as páginas do PDF
        mock_doc = MagicMock()
        
        page1 = MagicMock()
        page1.get_text.return_value = "Texto da página 1. \n"
        
        page2 = MagicMock()
        page2.get_text.return_value = "Texto da página 2."
        
        # Pagina vazia simulando uma imagem ou sem texto
        page3 = MagicMock()
        page3.get_text.return_value = "   "
        
        # O documento iterável retornará essas três páginas
        mock_doc.__iter__.return_value = [page1, page2, page3]
        
        # O mock.fitz_open retorna nosso documento falso
        mock_fitz_open.return_value = mock_doc

        resultado = extrair_elementos_peticao("caminho_falso.pdf")

        # Verifica se fitz.open foi chamado com o caminho correto
        mock_fitz_open.assert_called_once_with("caminho_falso.pdf")
        
        # Verifica se o doc.close foi chamado
        mock_doc.close.assert_called_once()
        
        # O resultado deve conter o texto stripado da página 1 e página 2 juntos
        # separados por \n\n
        expected_text = "Texto da página 1.\n\nTexto da página 2."
        self.assertEqual(resultado, expected_text)

    @patch('skills.extract_peticao.fitz.open')
    def test_extrair_elementos_peticao_falha_leitura(self, mock_fitz_open):
        # Simula erro ao abrir o arquivo
        mock_fitz_open.side_effect = Exception("Erro Corrompido Pela Metade")
        
        resultado = extrair_elementos_peticao("arquivo_corrompido.pdf")
        
        # Esperado que a exceção seja tratada e retorne uma string vazia
        self.assertEqual(resultado, "")

if __name__ == '__main__':
    unittest.main()
