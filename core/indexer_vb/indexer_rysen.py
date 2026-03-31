import os
import fitz  # PyMuPDF
import chromadb
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from fastembed import TextEmbedding
from dotenv import load_dotenv
from logger_config import setup_logger

# 1. Configurações Iniciais
load_dotenv()
logger = setup_logger("Indexer_Fast")

CHROMA_PATH = os.getenv("CHROMA_PATH", "./vector_db/jurisprudencia_2026")
# FastEmbed utiliza modelos locais leves. 
# O default é o BAAI/bge-small-en-v1.5, mas ele baixará automaticamente.
embedding_model = TextEmbedding() 

def process_single_pdf(pdf_info):
    """
    Função para extrair texto de um PDF. 
    Será executada em threads separadas.
    """
    pdf_path, filename = pdf_info
    chunks = []
    try:
        with fitz.open(pdf_path) as doc:
            for i, page in enumerate(doc):
                text = page.get_text().strip()
                if text:
                    # Criamos o chunk com metadados
                    chunks.append({
                        "id": f"{filename}_p{i}",
                        "text": text,
                        "metadata": {"fonte": filename, "pagina": i}
                    })
        return chunks
    except Exception as e:
        logger.error(f"Erro ao ler {filename}: {e}")
        return []

def popular_banco_dados_fast(pasta_origem, batch_size=32):
    """
    Popula o banco usando batches, fastembed e multithread.
    """
    # Inicializa Chroma
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name="jurisprudencia_2026")

    # Lista de arquivos
    if not os.path.exists(pasta_origem):
        os.makedirs(pasta_origem)
        return

    files = [(os.path.join(pasta_origem, f), f) for f in os.listdir(pasta_origem) if f.endswith(".pdf")]
    
    if not files:
        logger.warning("Nenhum PDF encontrado para indexação.")
        return

    # --- PASSO 1: Extração Multi-thread ---
    logger.info(f"Iniciando extração de texto de {len(files)} arquivos...")
    all_chunks = []
    with ThreadPoolExecutor(max_workers=4) as executor: # 4 workers é ideal para M1 8GB
        results = list(tqdm(executor.map(process_single_pdf, files), total=len(files), desc="Extraindo Textos"))
        for res in results:
            all_chunks.extend(res)

    # --- PASSO 2: Embedding e Inserção em Batches ---
    logger.info(f"Iniciando processamento de {len(all_chunks)} blocos em batches de {batch_size}...")
    
    for i in tqdm(range(0, len(all_chunks), batch_size), desc="Indexando no ChromaDB"):
        batch = all_chunks[i : i + batch_size]
        
        batch_texts = [item["text"] for item in batch]
        batch_ids = [item["id"] for item in batch]
        batch_metadatas = [item["metadata"] for item in batch]

        # FastEmbed gera os embeddings em lote de forma otimizada
        embeddings = list(embedding_model.embed(batch_texts))

        # Inserção no ChromaDB
        collection.add(
            ids=batch_ids,
            embeddings=embeddings,
            documents=batch_texts,
            metadatas=batch_metadatas
        )

    logger.info("✅ Base de Conhecimento atualizada com sucesso!")

if __name__ == "__main__":
    PASTA_JURIS = "./data/jurisprudencia"
    popular_banco_dados_fast(PASTA_JURIS)