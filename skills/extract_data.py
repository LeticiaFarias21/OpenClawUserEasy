import os
import fitz  # PyMuPDF
import ollama
import chromadb
from chromadb.config import Settings

# 1. Configuração do Banco de Dados Vetorial (Local)
# Ele criará uma pasta 'db_jurisprudencia' no seu diretório
client = chromadb.PersistentClient(path="./db_jurisprudencia")
collection = client.get_or_create_collection(name="jurisprudencia_2026")

def extract_text_chunks(pdf_path, chunk_size=1000):
    """Lê o PDF e quebra o texto em pedaços menores para o Nomic."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    
    # Quebra o texto em blocos de ~1000 caracteres (ajustável)
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def indexar_documentos(pasta_pdfs):
    """Processa todos os PDFs e envia para o nomic-embed-text."""
    print(f"📂 Iniciando indexação da pasta: {pasta_pdfs}")
    
    for arquivo in os.listdir(pasta_pdfs):
        if arquivo.endswith(".pdf"):
            caminho_completo = os.path.join(pasta_pdfs, arquivo)
            chunks = extract_text_chunks(caminho_completo)
            
            for i, chunk in enumerate(chunks):
                # Gerar o Embedding usando o Nomic via Ollama
                response = ollama.embeddings(
                    model="nomic-embed-text",
                    prompt=chunk
                )
                embedding = response["embedding"]
                
                # Salvar no ChromaDB
                collection.add(
                    ids=[f"{arquivo}_{i}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"fonte": arquivo, "pagina": i}]
                )
            print(f"✅ Arquivo indexado: {arquivo}")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    # Certifique-se de criar essa pasta e colocar alguns PDFs lá
    PASTA_JURISPRUDENCIA = "./data/jurisprudencia"
    
    if not os.path.exists(PASTA_JURISPRUDENCIA):
        os.makedirs(PASTA_JURISPRUDENCIA)
        print(f"⚠️ Pasta {PASTA_JURISPRUDENCIA} criada. Coloque seus PDFs lá e rode novamente.")
    else:
        indexar_documentos(PASTA_JURISPRUDENCIA)
        print("\n🚀 Base de Conhecimento pronta para consulta!")