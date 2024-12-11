from unittest.mock import patch
from src.sms_disease_alert.tools.telegram_tool import TelegramBotTool, TelegramBotInput

@patch('tools.telegram_tool.requests.post')
def test_telegram_bot_tool(mock_post):
    tool = TelegramBotTool()
    input_data = TelegramBotInput(message="Test message", chat_id="12345")

    # Simular uma resposta bem-sucedida do Telegram
    mock_post.return_value.status_code = 200

    result = tool._run(**input_data.dict())

    assert result == "Notification sent successfully.", "Deve retornar que a notificação foi enviada com sucesso"
    mock_post.assert_called_once()