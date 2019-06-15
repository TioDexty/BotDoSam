#coding: utf-8
#!/usr/bin/python3.7
#Bot do Sam
#@AcervoDoSam
#@GrupoDoSam

from telegram.ext import Updater, CommandHandler
import logging

API_TOKEN = 'TOKEN @BOTFATHER'

logging.basicConfig(level=logging.INFO)

def regras(bot, update):
  """Envia as regras quando algum usuário enviar /regras."""
	regras = """
<b>1.</b> Não envie ou peça qualquer tipo de pornografia;
<b>2.</b> Não envie ou peça qualquer tipo de conteúdo extremo, seja ele gore, scat ou outro;
<b>3.</b> Não envie ou peça qualqeur tipo de informação pessoal ("dox"/"exposed");
<b>4.</b> Off-topic é permitido, contanto que seja moderado;
<b>5.</b> Se você tem alguma sugestão, envie-a, no privado, para algum administrador ou moderador;
<b>6.</b> Não cometa flood, não envie muitas mensagens pequenas, não abuse de GIFs e stickers. Se você foi banido, não pergunte o por quê por outra conta. A resposta será "por flood";
<b>7.</b> Não compartilhe nenhum APK ou executável, a não ser que alguém tenha requisitado isso;
<b>8.</b> Não espere atenção 24/7 do administrador ou moderador;
<b>9.</b> Proibido qualquer tipo de preconceito, exceto com fstring em python; e
<b>10.</b> Não enviar links suspeitos nem links de grupos/canais do Telegram, apenas com autorização de um administrador ou moderador.
"""
	bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=regras)

def main():
	updater = Updater(token=API_TOKEN)
	dispatcher = updater.dispatcher

	dispatcher.add_handler(CommandHandler('regras', regras))
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()
