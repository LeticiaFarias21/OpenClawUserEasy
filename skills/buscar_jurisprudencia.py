import ollama
import collection

def buscar_jurisprudencia(pergunta_usuario):
    # 1. Transforma a pergunta em vetor usando o mesmo Nomic
    query_embedding = ollama.embeddings(model="nomic-embed-text", prompt=pergunta_usuario)["embedding"]
    
    # 2. Busca os 2 documentos mais parecidos no banco
    resultados = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    return resultados["documents"][0]