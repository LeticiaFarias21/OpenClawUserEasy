import os
from dotenv import load_dotenv

load_dotenv()

def create_openclaw_agent(name, role, goal, workflow_steps, model=None):
    """
    Gera um ficheiro .md de identidade para o OpenClaw na pasta 'agentes/'.
    """
    # 1. Definir e criar a pasta de destino
    target_dir = "agentes"
    os.makedirs(target_dir, exist_ok=True)
    
    agent_model = model or os.getenv("OPENCLAW_TRIAGE_MODEL", "llama3.2:3b")
    workflow_md = "\n".join([f"{i+1}. {step}" for i, step in enumerate(workflow_steps)])
    
    template = f"""# Identity: {name}
- **Role**: {role}
- **Model**: {agent_model}
- **Goal**: {goal}

## Workflow
{workflow_md}

## Skills
- Use `python:../skills/extract_data.py` para processamento de texto.
- Base de Conhecimento: Jurisprudência TJ/2026.
"""

    # 2. Definir o caminho completo (pasta + nome do ficheiro)
    filename = os.path.join(target_dir, f"{name.replace(' ', '_')}.md")
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(template)
        print(f"✅ Agente '{name}' criado com sucesso em: {filename}")
    except Exception as e:
        print(f"❌ Erro ao criar agente: {e}")