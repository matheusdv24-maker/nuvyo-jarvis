import os
import json
from flask import Flask, request
import telebot
from google import genai
from google.genai import types

# 1. Configuração de segurança
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 2. Inicializando os sistemas
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Criamos um aplicativo web mini para receber as mensagens da "campainha"
app = Flask(__name__)

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

# 5. Configuração para processar a mensagem recebida
@bot.message_handler(func=lambda message: True)
def responder_mensagem(message):
    resposta_jarvis = obter_resposta_jarvis(message.text)
    bot.reply_to(message, resposta_jarvis)

# 6. A "Campainha": O Telegram envia a mensagem para cá
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "Jarvis está operacional.", 200
