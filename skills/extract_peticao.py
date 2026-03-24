import fitz  # PyMuPDF
from core.logger_config import setup_logger

logger = setup_logger("Extractor_Text_Only")

def extrair_elementos_peticao(pdf_path):
    """
    Extrai apenas o conteúdo de texto do PDF, ignorando imagens e elementos visuais.
    Ideal para processamento rápido e baixo consumo de RAM.
    """
    logger.info(f"Iniciando extração simplificada (apenas texto) de: {pdf_path}")
    conteudo_final = []
    
    try:
        # Abre o documento PDF
        doc = fitz.open(pdf_path)
        
        for page_num, page in enumerate(doc):
            # Extrai o texto da página atual
            texto = page.get_text().strip()
            
            if texto:
                conteudo_final.append(texto)
                logger.debug(f"Texto extraído da página {page_num + 1}")
            else:
                logger.warning(f"Página {page_num + 1} parece estar vazia ou conter apenas imagens.")

        doc.close()
        
        # Junta todo o texto extraído com quebras de linha entre as páginas
        return "\n\n".join(conteudo_final)

    except Exception as e:
        logger.error(f"Falha ao processar o PDF {pdf_path}: {e}")
        return ""

if __name__ == "__main__":
    # Teste rápido de extração
    caminho_teste = "./data/peticoes/exemplo.pdf"
    resultado = extrair_elementos_peticao(caminho_teste)
    print(resultado)