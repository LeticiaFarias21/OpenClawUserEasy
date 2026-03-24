from core.logger_config import setup_logger

logger = setup_logger("OllamaAgent")

class OllamaAgent:
    def __init__(self, name, role, model="qwen3.5:0.8b"):
        self.name = name
        self.role = role
        self.model = model
        self.base_url = "http://localhost:11434/api/chat"
        logger.info(f"Agente {self.name} inicializado com o modelo {self.model}")

    def receive_message(self, message, sender_name):
        logger.debug(f"Mensagem recebida por {self.name} de {sender_name}")
        prompt = f"Você é um {self.role}. Recebeu a seguinte informação: {message}. Responda de forma técnica e concisa."
        return self.ask_ollama(prompt)

    def ask_ollama(self, prompt):
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        try:
            logger.debug(f"Chamando Ollama API para o agente {self.name}")
            response = requests.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()
            content = response.json()['message']['content']
            logger.info(f"Resposta recebida com sucesso para o agente {self.name}")
            return content
        except Exception as e:
            logger.error(f"Erro na comunicação do agente {self.name}: {str(e)}")
            return f"Erro na comunicação: {str(e)}"