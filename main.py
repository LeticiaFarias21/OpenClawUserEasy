import os
from dotenv import load_dotenv
import requests
import json
from core.logger_config import setup_logger
from core.ollamaAgent import OllamaAgent
# Carrega as variáveis do arquivo .env
load_dotenv()
logger = setup_logger("Orchestrator")
# Agora você acessa assim:
primary_model = os.getenv("OPENCLAW_PRIMARY_MODEL")
ollama_url = os.getenv("OLLAMA_HOST")

print(f"🤖 Sistema iniciado com o modelo: {primary_model}")


def executar_fluxo_juridico(peticao_inicial):
    # Uso dos modelos otimizados para M1 8GB
    agente_triagem = OllamaAgent("Agente_Triagem", "Especialista em Triagem", model="llama3.2:3b")
    agente_analista = OllamaAgent("Agente_Jurisprudencia", "Analista", model="qwen2.5:3b")

    logger.info("Iniciando fluxo jurídico multi-agente")
    
    resultado_triagem = agente_triagem.receive_message(peticao_inicial, "Protocolo")
    analise_final = agente_analista.receive_message(resultado_triagem, "Agente_Triagem")
    
    logger.info("Fluxo finalizado com sucesso")
    return analise_final