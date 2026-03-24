import requests
import json

class OllamaAgent:
    def __init__(self, name, role, model="qwen3.5:0.8b"):
        self.name = name
        self.role = role
        self.model = model
        self.base_url = "http://localhost:11434/api/chat"
        self.memory = []

    def receive_message(self, message, sender_name):
        print(f"\n[SISTEMA]: {self.name} recebeu dados de {sender_name}...")
        prompt = f"Você é um {self.role}. Recebeu a seguinte informação: {message}. Responda de forma técnica e concisa para o próximo passo do processo jurídico."
        return self.ask_ollama(prompt)

    def ask_ollama(self, prompt):
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        try:
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            return response.json()['message']['content']
        except Exception as e:
            return f"Erro na comunicação com Ollama: {str(e)}"

# --- Orquestração do Fluxo do Tribunal ---

def executar_fluxo_juridico(peticao_inicial):
    # Instanciando os Agentes (usando os modelos otimizados para seu M1)
    agente_triagem = OllamaAgent("Agente_Triagem", "Especialista em Triagem Processual do TJ", model="llama3.2:3b")
    agente_analista = OllamaAgent("Agente_Jurisprudencia", "Analista de Jurisprudência e Precedentes", model="qwen2.5:3b")

    print(f"🚀 Iniciando Fluxo Multi-Agente para Petição...")

    # Passo 1: Triagem
    print(f"\n--- PASSO 1: TRIAGEM ---")
    resultado_triagem = agente_triagem.receive_message(peticao_inicial, "Protocolo Geral")
    print(f"[{agente_triagem.name}]: {resultado_triagem}")

    # Passo 2: Analista recebe da Triagem (Cruzamento de dados)
    print(f"\n--- PASSO 2: ANÁLISE DE PRECEDENTES ---")
    analise_final = agente_analista.receive_message(resultado_triagem, agente_triagem.name)
    print(f"[{agente_analista.name}]: {analise_final}")

    return analise_final

# --- Exemplo de Uso ---
if __name__ == "__main__":
    exemplo_peticao = """
    Ação de Indenização por Danos Morais contra a Cia Aérea X por atraso de 12 horas 
    em voo internacional. O autor pleiteia R$ 15.000,00.
    """
    executar_fluxo_juridico(exemplo_peticao)