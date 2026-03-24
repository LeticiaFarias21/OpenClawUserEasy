import os
import chromadb
from fastembed import TextEmbedding
from dotenv import load_dotenv
from core.logger_config import setup_logger

# Carrega as configurações do .env
load_dotenv()
logger = setup_logger("Search_Skill")

# Configurações do Banco de Dados e Modelo (Consistente com o Indexer)
CHROMA_PATH = os.getenv("CHROMA_PATH", "./vector_db/jurisprudencia_2026")
# Inicializa o FastEmbed (utiliza o mesmo modelo padrão do indexador)
embedding_model = TextEmbedding()

NOME_DO_BANCO="jurisprudencia_2026"

def buscar_jurisprudencia(pergunta_usuario, n_resultados=3):
    """
    Realiza a busca semântica na base de jurisprudência utilizando FastEmbed.
    """
    try:
        # 1. Conectar ao ChromaDB
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_or_create_collection(name=NOME_DO_BANCO)

        logger.info(f"🔎 Realizando busca semântica para: '{pergunta_usuario[:50]}...'")

        # 2. Gerar o embedding da pergunta usando FastEmbed
        # O modelo espera uma lista e retorna um iterador
        query_embeddings = list(embedding_model.embed([pergunta_usuario]))
        query_vector = query_embeddings[0]

        # 3. Consultar o banco de dados
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=n_resultados
        )

        # 4. Formatar os resultados para o Agente
        if not results["documents"] or not results["documents"][0]:
            logger.warning("Nenhum resultado relevante encontrado na base.")
            return "Nenhuma jurisprudência relevante encontrada para este caso."

        contexto = "\n\n--- TRECHO RELEVANTE ---\n".join(results["documents"][0])
        logger.info("✅ Contexto jurídico recuperado com sucesso.")
        
        return contexto

    except Exception as e:
        logger.error(f"Erro ao buscar jurisprudência: {e}")
        return f"Erro técnico ao aceder à base de conhecimento: {e}"

if __name__ == "__main__":
    # Teste rápido de consulta
    teste_pergunta = "Direito do consumidor, atraso de voo e danos morais"
    print(buscar_jurisprudencia(teste_pergunta))