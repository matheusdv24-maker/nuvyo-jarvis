import os
import telebot
from google import genai
from google.genai import types

# 1. Configuração de segurança (As chaves agora ficam escondidas no servidor)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 2. Inicializando os sistemas
bot = telebot.TeleBot(TELEGRAM_TOKEN)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# 3. Personalidade do seu assistente
jarvis_prompt = """
Você é o Jarvis, um assistente pessoal ultra-inteligente, focado em produtividade, finanças e organização de rotina.
Você foi criado pelo Matheus Dias Vieira. Sempre que falar com ele, trate-o com respeito, de forma direta, prestativa e com um tom levemente formal ou sutilmente irônico, igual ao assistente do Homem de Ferro.
Sua missão é ajudar o usuário a gerenciar a vida dele.
"""

# 4. Função para conversar com a IA do Gemini
def obter_resposta_jarvis(mensagem_usuario):
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=mensagem_usuario,
            config=types.GenerateContentConfig(
                system_instruction=jarvis_prompt,
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e:
        return f"Desculpe, Senhor. Houve uma falha no meu sistema de IA: {e}"

# 5. Configuração para receber as mensagens do Telegram
@bot.message_handler(func=lambda message: True)
def responder_mensagem(message):
    print(f"O Senhor me mandou: {message.text}")
    
    # Busca a resposta com a IA
    resposta_jarvis = obter_resposta_jarvis(message.text)
    
    # Envia de volta para o seu Telegram
    bot.reply_to(message, resposta_jarvis)

# 6. Comando para ligar o robô
if __name__ == "__main__":
    print("Sistemas iniciados. Jarvis está online e aguardando comandos no Telegram...")
    bot.infinity_polling()
