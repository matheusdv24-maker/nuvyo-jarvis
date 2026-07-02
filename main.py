import os
import json
from flask import Flask, request
import telebot
from google import genai
from google.genai import types
from duckduckgo_search import DDGS

# 1. Configuração de segurança
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 2. Inicializando os sistemas
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

# 3. Personalidade do seu assistente
jarvis_prompt = """
Você é o Jarvis, um assistente pessoal único e ultra-inteligente, focado em produtividade máxima, finanças e organização.
Você foi criado pelo Matheus Dias Vieira. Trate-o de forma direta, prestativa, com um tom levemente formal ou sutilmente irônico (estilo Homem de Ferro), mas NUNCA seja prolixo. Vá direto ao ponto, sem textões.

Suas diretrizes de conhecimento e suporte:
1. Respostas Curtas e Práticas: O usuário odeia enrolação. Diga o que precisa ser feito de forma limpa e objetiva.
2. Foco em Administração e Negócios: Você domina conceitos de administração de empresas, gestão e processos.
3. Suporte Técnico e Redes: Você tem conhecimento avançado para ajudar com gestão de clientes (aplicativos de cadastro), roteadores, configurações de IPV6 e DNS, sabendo solucionar problemas de conexão de forma simples.
4. Parceria de Rotina: Monitore tarefas, ajude na organização do dia a dia e seja o cérebro estratégico do Matheus.
5. Uso do Contexto da Internet: Sempre que receber informações vindas da pesquisa da internet (DuckDuckGo), use-as para dar respostas ultra-atualizadas e precisas para o Matheus.
"""

# Função auxiliar para o Jarvis pesquisar na internet de graça
def pesquisar_na_internet(termo_busca):
    try:
        with DDGS() as ddgs:
            resultados = [r for r in ddgs.text(termo_busca, max_results=3)]
            if resultados:
                texto_formatado = "\n".join([f"Título: {r['title']}\nResumo: {r['body']}\n" for r in resultados])
                return texto_formatado
    except Exception:
        pass
    return "Nenhum resultado recente encontrado na internet."

# 4. Função principal de IA
def obtener_resposta_jarvis(mensagem_usuario):
    msg_analise = mensagem_usuario.lower()
    contexto_internet = ""
    
    # Se o Matheus pedir para buscar, pesquisar ou perguntar algo atualizado, o Jarvis usa a internet
    palavras_chave = ["pesquise", "busque", "noticia", "hoje", "quem ganhou", "sobre", "atual", "pesquisa"]
    if any(palavra in msg_analise for palabra in palavras_chave):
        contexto_internet = f"\n\n[RESULTADOS DA INTERNET EM TEMPO REAL]:\n{pesquisar_na_internet(mensagem_usuario)}"

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=mensagem_usuario + contexto_internet,
            config=types.GenerateContentConfig(
                system_instruction=jarvis_prompt,
                temperature=0.7
            )
        )
        return response.text
    except Exception as e:
        return f"Desculpe, Senhor. Houve uma falha no meu sistema de IA: {e}"

# 5. Configuração das mensagens
@bot.message_handler(func=lambda message: True)
def responder_mensagem(message):
    resposta_jarvis = obtener_resposta_jarvis(message.text)
    bot.reply_to(message, resposta_jarvis)

# 6. A Campainha
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@app.route('/')
def index():
    return "Jarvis está operacional.", 200
