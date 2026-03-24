import os
from dotenv import load_dotenv

# Carrega as configurações do seu .env
load_dotenv()

def create_openclaw_agent(name, role, goal, workflow_steps, model=None):
    """
    Gera um arquivo .md de identidade para o OpenClaw.
    """
    # Se não passar modelo, usa o default de triagem do .env (Llama 3.2 3B)
    agent_model = model or os.getenv("OPENCLAW_TRIAGE_MODEL", "ollama/llama3.2:3b")
    
    # Formata os passos do workflow em lista Markdown
    workflow_md = "\n".join([f"{i+1}. {step}" for i, step in enumerate(workflow_steps)])
    
    template = f"""# Identity: {name}
    - **Role**: {role}
    - **Model**: {agent_model}
    - **Goal**: {goal}

    ## Workflow
    {workflow_md}

    ## Skills
    - Use `python:skills/extract_data.py` para processamento de texto.
    - Base de Conhecimento: Jurisprudência TJ/2026.
    """

    # Nome do arquivo baseado no nome do agente
    filename = f"{name.replace(' ', '_')}.md"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(template)
        print(f"✅ Agente '{name}' criado com sucesso em: {filename}")
    except Exception as e:
        print(f"❌ Erro ao criar agente: {e}")

# --- EXEMPLO DE USO PARA O TRIBUNAL DE JUSTIÇA ---
if __name__ == "__main__":
    # Parâmetros para um novo agente de "Análise de Custas"
    params = {
        "name": "Agente de Custas",
        "role": "Contador Judicial Automatizado",
        "goal": "Verificar se as custas processuais foram pagas corretamente conforme a tabela do Tribunal.",
        "workflow_steps": [
            "Localizar a guia de pagamento no PDF.",
            "Extrair o valor pago e o código de barras.",
            "Comparar com o valor da causa informado na petição.",
            "Emitir parecer de 'Custas Satisfeitas' ou 'Diligência Necessária'."
        ],
        "model": os.getenv("OPENCLAW_PRIMARY_MODEL")  # Qwen é melhor para números/lógica
    }

    create_openclaw_agent(**params)