import os
import fitz  # PyMuPDF
import ollama
import chromadb
from dotenv import load_dotenv
from logger_config import setup_logger

# Carrega configurações do .env
load_dotenv()
logger = setup_logger("Indexer")

# Configurações do Banco de Dados Vetorial
CHROMA_PATH = os.getenv("CHROMA_PATH", "./vector_db/jurisprudencia_2026")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

def extrair_e_limpar_texto(pdf_path):
    """Extrai texto do PDF e remove espaços desnecessários."""
    texto_completo = ""
    try:
        with fitz.open(pdf_path) as doc:
            for pagina in doc:
                texto_completo += pagina.get_text()
        return texto_completo.strip()
    except Exception as e:
        logger.error(f"Erro ao ler PDF {pdf_path}: {e}")
        return ""

def criar_chunks(texto, tamanho=1000, sobreposicao=100):
    """Divide o texto em blocos menores para o modelo Nomic."""
    chunks = []
    for i in range(0, len(texto), tamanho - sobreposicao):
        chunks.append(texto[i:i + tamanho])
    return chunks

def popular_banco_dados(pasta_origem):
    """Processa PDFs e envia para o ChromaDB via Nomic Embed."""
    # Inicializa o cliente Chroma
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name="jurisprudencia_2026")

    if not os.path.exists(pasta_origem):
        logger.warning(f"Pasta {pasta_origem} não encontrada. Criando...")
        os.makedirs(pasta_origem)
        return

    ficheiros = [f for f in os.listdir(pasta_origem) if f.endswith(".pdf")]
    logger.info(f"Encontrados {len(ficheiros)} ficheiros para indexação.")

    for nome_ficheiro in ficheiros:
        caminho_pdf = os.path.join(pasta_origem, nome_ficheiro)
        logger.info(f"Processando: {nome_ficheiro}")

        texto = extrair_e_limpar_texto(caminho_pdf)
        blocos = criar_chunks(texto)

        for i, bloco in enumerate(blocos):
            try:
                # Gera o embedding usando o Nomic via Ollama
                res = ollama.embeddings(model=EMBEDDING_MODEL, prompt=bloco)
                vetor = res["embedding"]

                # Adiciona ao banco
                collection.add(
                    ids=[f"{nome_ficheiro}_chunk_{i}"],
                    embeddings=[vetor],
                    documents=[bloco],
                    metadatas=[{"fonte": nome_ficheiro, "parte": i}]
                )
            except Exception as e:
                logger.error(f"Erro ao indexar bloco {i} de {nome_ficheiro}: {e}")

    logger.info("✅ Indexação concluída com sucesso!")

if __name__ == "__main__":
    PASTA_PDFS = "./data/jurisprudencia"
    popular_banco_dados(PASTA_PDFS)