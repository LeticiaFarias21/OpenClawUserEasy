import os
import requests
from dotenv import load_dotenv
from core.logger_config import setup_logger
from core.ollamaAgent import OllamaAgent
from core.agent_factory import create_openclaw_agent
from skills.buscar_jurisprudencia import buscar_jurisprudencia
from skills.extract_peticao import extrair_elementos_peticao

# 1. Configuração Inicial e Logs
load_dotenv()
logger = setup_logger("Orchestrator")

def preparar_agentes():
    """Garante que as identidades OpenClaw (.md) estejam criadas e atualizadas."""
    logger.info("Verificando identidades dos agentes no diretório 'agentes/'...")
    
    # Parâmetros para o Agente de Triagem
    triagem_params = {
        "name": "Agente_Triagem",
        "role": "Especialista em Triagem Processual do TJ",
        "goal": "Analisar a petição inicial e classificar o tipo de ação.",
        "workflow_steps": [
            "Receber o texto do PDF.",
            "Identificar: Tipo de Ação, Valor da Causa e Partes.",
            "Enviar resumo para o Agente_Analista."
        ],
        "model": os.getenv("OPENCLAW_TRIAGE_MODEL")
    }

    # Parâmetros para o Agente Analista
    analista_params = {
        "name": "Agente_Analista",
        "role": "Pesquisador jurídico focado em precedentes.",
        "goal": "Enriquecer a análise com jurisprudência real do TJ/2026.",
        "workflow_steps": [
            "Receber os dados da triagem.",
            "Utilizar a Skill 'buscar_jurisprudencia.py' para encontrar casos similares.",
            "Comparar a petição com os resultados encontrados pelo Nomic Embed.",
            "Sugerir minuta baseada em factos e precedentes reais."
        ],
        "model": os.getenv("OPENCLAW_PRIMARY_MODEL")
    }

    # Criando os arquivos .md via Factory
    os.makedirs("agentes", exist_ok=True)
    create_openclaw_agent(**triagem_params)
    create_openclaw_agent(**analista_params)

def executar_fluxo_juridico(peticao_inicial):
    """Executa o fluxo utilizando as identidades gerenciadas pelo OpenClaw."""
    
    # Instanciando Agentes (Eles agora usam os modelos definidos nos arquivos .md gerados)
    agente_triagem = OllamaAgent(
        "Agente_Triagem", 
        "Especialista em Triagem, para infomações necessárias para a petição ocorrer", 
        model=os.getenv("OPENCLAW_PRIMARY_MODEL")
    )
    agente_analista = OllamaAgent(
        "Agente_Analista", 
        "Analista de Jurisprudência", 
        model=os.getenv("OPENCLAW_PRIMARY_MODEL")
    )

    logger.info("🚀 Iniciando fluxo jurídico multi-agente")
    
    # Passo 1: Triagem básica
    resumo_triagem = agente_triagem.receive_message(peticao_inicial, "Protocolo")

    # Passo INTERMEDIÁRIO: O uso do Nomic Embed para RAG
    logger.info("🔎 Consultando Base de Conhecimento via Nomic Embed...")
    jurisprudencia_relevante = buscar_jurisprudencia(resumo_triagem)

    # Passo 2: O Analista recebe o resumo E a jurisprudência real
    prompt_enriquecido = f"DADOS DA PETIÇÃO: {resumo_triagem}\n\nJURISPRUDÊNCIA ENCONTRADA: {jurisprudencia_relevante}"
    
    analise_final = agente_analista.receive_message(prompt_enriquecido, "Agente_Triagem + NomicSearch")
    
    return analise_final

if __name__ == "__main__":
    # Garantir que os agentes (.md) existam antes de rodar
    preparar_agentes()
    
    caminho_pdf = "./data/jurisprudencia/peticao/petição.pdf"

    if os.path.exists(caminho_pdf):
        resultado = executar_fluxo_juridico(extrair_elementos_peticao(caminho_pdf))
        print(f"\n--- PARECER DO SISTEMA ---\n{resultado}")
    else:
        logger.error(f"Ficheiro não encontrado: {caminho_pdf}")