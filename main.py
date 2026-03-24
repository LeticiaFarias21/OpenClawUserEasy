import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Agora você acessa assim:
primary_model = os.getenv("OPENCLAW_PRIMARY_MODEL")
ollama_url = os.getenv("OLLAMA_HOST")

print(f"🤖 Sistema iniciado com o modelo: {primary_model}")