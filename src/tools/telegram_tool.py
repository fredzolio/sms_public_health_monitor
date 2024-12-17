import os
from crewai.tools import BaseTool
from typing import ClassVar, Type
from pydantic import BaseModel, Field
import requests
import logging

# Configuração do logger para capturar mensagens de erro ou informações importantes
logging.basicConfig(level=logging.INFO)

class TelegramBotInput(BaseModel):
    """Input schema for TelegramBotTool."""
    message: str = Field(..., description="Message to send via Telegram.")
    chat_id: str = Field(..., description="Chat ID to send the message to.")
    
    class Config:
        arbitrary_types_allowed = True

class TelegramBotTool(BaseTool):
    name: str = "TelegramBotTool"
    description: str = (
        "This tool sends messages using Telegram Bot API to notify authorities or citizens."
    )
    args_schema: Type[BaseModel] = TelegramBotInput

    TELEGRAM_BOT_TOKEN: ClassVar[str] = os.getenv("TELEGRAM_BOT_TOKEN")

    def _run(self, message: str, chat_id: str) -> str:
        # Verificar se o token do Telegram foi configurado corretamente
        if self.TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here" or not self.TELEGRAM_BOT_TOKEN:
            error_message = "Erro: O token do bot do Telegram não foi configurado corretamente."
            logging.error(error_message)
            return error_message

        url = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message
        }

        try:
            # Enviar a mensagem utilizando a API do Telegram
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                logging.info("Notificação enviada com sucesso para o chat_id %s.", chat_id)
                return "Notificação enviada com sucesso."
            else:
                logging.error(f"Erro ao enviar notificação: {response.status_code} - {response.text}")
                return f"Erro ao enviar notificação: {response.text}"

        except requests.exceptions.RequestException as e:
            # Capturar qualquer exceção que ocorra durante o envio da requisição
            logging.error(f"Erro de requisição ao enviar notificação: {str(e)}")
            return f"Erro ao enviar notificação: {str(e)}"

