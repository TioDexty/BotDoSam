#coding: utf-8
#!/usr/bin/python3.7
#Bot do Sam
#@AcervoDoSam
#@GrupoDoSam

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import NetworkError, Unauthorized, BadRequest
import logging
import requests
import json
import shodan
import random
import sys
import os
import re
import socket

API_TOKEN = os.getenv('TOKEN')

modo = os.getenv('MODO')

shod_key1 = os.getenv('SHODAN_1')
shod_key2 = os.getenv('SHODAN_2')

shodan_keys = []

shodan_keys.append(shod_key1)
shodan_keys.append(shod_key2)

####
canal = ['https://t.me/AcervoDoSam', '@AcervoDoSam']
####

logging.basicConfig(level=logging.INFO)

if modo == 'dev':
	def rodar(updater):
		updater.start_polling()
		updater.idle()

elif modo == 'prod':
	def rodar(updater):
		PORTA = int(os.environ.get('PORT', '8443'))
		HEROKU_NOME = os.environ.get('HEROKU_APP_NAME')

		updater.start_webhook(listen='0.0.0.0',
								port=PORTA,
								url_path=TOKEN)
		updater.bot.set_webhook('https://{}.herokuapp.com/{}'.format(HEROKU_NOME, TOKEN))
else:
	logger.error('MODO NÃO ESPECIFICADO')
	sys.exit()

def check_adm(user_id, admin_list):
	for adm in admin_list:
		adm_id = adm.user.id
		if adm_id == user_id:
			return True
	return False

def bvindas(bot, update):
	for m in update.message.new_chat_members:
		boasvindas = '<b>Olá, {}. Bem-vindo(a) ao, {}.</b>'.format(m.first_name, update.message.chat.title)
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=boasvindas)	

def info(bot, update):
	info_txt = """
<b>Olá, sou o bot do Sam, fui criado para administrar o canal e o grupo do @SamMarx.</b>

<b>Desenvolvedor: </b> <a href="http://t.me/SamMarx">Sam</a>.
<b>Código: </b> <a href="http://github.com/Sam-Marx/BotDoSam">Github</a>.
"""

	bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=info_txt, reply_to_message_id=update.message.message_id)

def admin(bot, update):
	try:
		admins = bot.get_chat_administrators(chat_id=update.message.chat_id)

		msg = """
Administradores:

{}""".format(admins)
		print(bot.get_chat_administrators(chat_id=update.message.chat_id))

		bot.send_message(chat_id=update.message.chat_id, text=msg, reply_to_message_id=update.message.message_id)
	except BadRequest as e:
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Erro: </b>{}'.format(e), reply_to_message_id=update.message.message_id)

def link(bot, update):
	cnl = random.choice(canal)

	try:
		msg = """
<b>Link do grupo: </b>{}
<b>Link do canal: </b>{}
	""".format(bot.export_chat_invite_link(chat_id=update.message.chat_id),cnl)

		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=msg, reply_to_message_id=update.message.message_id)
	except BadRequest as e:
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Erro: </b>{}\n\nTalvez eu precise de permissões de administrador para executar este comando.'.format(e), reply_to_message_id=update.message.message_id)

def gp(bot, update):
	id_data = str(bot.get_chat(chat_id=update.message.chat_id))

	id_data = re.sub("'", '"', id_data)
	js = json.loads(id_data)

	msg = """
<b>Informações atuais do grupo</b>

<b>ID:</b> {}
<b>Tipo:</b> {}

<b>Título:</b> {}
<b>Número de membros:</b> {}
""".format(js['id'], js['type'], js['title'], bot.get_chat_members_count(chat_id=update.message.chat_id))

	bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=msg, reply_to_message_id=update.message.message_id)

def honeypot(bot, update, args):
	try:
		args[0] = socket.gethostbyname(args[0])

		key = random.choice(shodan_keys)

		api = shodan.Shodan(key)

		honey_text = """
<b>Honeypot</b>
<b>IP: </b>{}

Calculando a probabilidade do endereço ser uma honeypot...

1.0 = honeypot
0.0 = não é uma honeypot
"""

		msg = bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=honey_text.format(args[0]), reply_to_message_id=update.message.message_id)

		honey_request = requests.get('https://api.shodan.io/labs/honeyscore/{}?key={}'.format(args[0], key))

		if float(honey_request.text) > 0.5:
			novo_texto = """
<b>Honeypot</b>
<b>IP: </b>{}

A probabilidade do endereço ser uma honeypot é <b>grande</b>: {}

1.0 = honeypot
0.0 = não é uma honeypot
""".format(args[0], honey_request.text)

		else:
			novo_texto = """
<b>IP: </b>{}

A probabilidade do endereço ser uma honeypot é <b>pequena</b>: {}

1.0 = honeypot
0.0 = não é uma honeypot
""".format(args[0], honey_request.text)

		bot.edit_message_text(parse_mode='HTML', chat_id=update.message.chat_id, message_id=msg.message_id, text=novo_texto)

	except IndexError:
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='/honeypot <b>IP</b>/<b>DOMÍNIO</b> para obter o resultado.', reply_to_message_id=update.message.message_id)

def ip(bot, update, args):
	try:
		args[0] = socket.gethostbyname(args[0])

		key = random.choice(shodan_keys)

		api = shodan.Shodan(key)

		ip_text = """
<b>IP: </b>{} sendo escaneado.

Voltarei com os resultados assim que possível."""

		msg = bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=ip_text.format(args[0]), reply_to_message_id=update.message.message_id)

		try:
			geo_ip = requests.get('http://ip-api.com/json/{}'.format(args[0]))

			geo_ip_json = json.loads(geo_ip.text)

			asn = geo_ip_json['as']
			cidade = geo_ip_json['city']
			pais =geo_ip_json['country']
			codigoPais = geo_ip_json['countryCode']
			isp = geo_ip_json['isp']
			lat = geo_ip_json['lat']
			lon = geo_ip_json['lon']

			host = api.host(args[0])

			novo_texto = """
<b>IP: </b>{}
<b>Hospedado por: </b>{}
<b>País: </b>{} - {}
<b>Cidade: </b>{}
<b>ISP: </b>{}
<b>Latitude: </b>{}
<b>Longitude: </b>{}

<b>Organização: </b>{}
<b>Sistema operacional: </b>{}
<b>Portas: </b>{}
"""	

			bot.edit_message_text(parse_mode='HTML', chat_id=update.message.chat_id, 
				message_id=msg.message_id, 
				text=novo_texto.format(
					args[0],
					asn,
					pais, codigoPais,
					cidade,
					isp,
					lat,
					lon,
					host.get('org', 'n/a'), 
					host.get('os', 'n/a'), 
					host.get('ports', 'n/a')))

		except shodan.APIError as e:
			err_t = "<b>Erro com o IP {}: </b>{}".format(args[0], e)
			bot.edit_message_text(parse_mode='HTML', chat_id=update.message.chat_id, message_id=msg.message_id, text=err_t)

		except BadRequest as e:
			err_t = "<b>Erro: </b>{}\n\nTente novamente mais tarde.".format(e)
			bot.edit_message_text(parse_mode='HTML', chat_id=update.message.chat_id, message_id=msg.message_id, text=err_t)

		except Exception as e:
			print('Erro: ' + str(e))

	except IndexError:
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='/ip <b>IP</b>/<b>DOMÍNIO</b> para obter informações sobre o endereço.', reply_to_message_id=update.message.message_id)

def regras(bot, update):
	regras = """
<b>1.</b> Não envie ou peça qualquer tipo de pornografia;
<b>2.</b> Não envie ou peça qualquer tipo de conteúdo extremo, seja ele gore, scat ou outro;
<b>3.</b> Não envie ou peça qualquer tipo de informação pessoal ("dox"/"exposed");
<b>4.</b> Off-topic é permitido, contanto que seja moderado;
<b>5.</b> Se você tem alguma sugestão, envie-a, no privado, para algum administrador ou moderador;
<b>6.</b> Não cometa flood, não envie muitas mensagens pequenas, não abuse de GIFs e stickers. Se você foi banido, não pergunte o por quê por outra conta. A resposta será "por flood";
<b>7.</b> Não compartilhe nenhum APK ou executável, a não ser que alguém tenha requisitado isso;
<b>8.</b> Não espere atenção 24/7 do administrador ou moderador;
<b>9.</b> Proibido qualquer tipo de preconceito, exceto com fstring em python; e
<b>10.</b> Não enviar links suspeitos nem links de grupos/canais do Telegram, apenas com autorização de um administrador ou moderador.
"""
	bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=regras, reply_to_message_id=update.message.message_id)

def ajuda(bot, update):
	ajuda = """
/ip <b>IP</b> - Mostra informações sobre o endereço IP
/regras - Envia a lista de regras do grupo
/honeypot <b>IP</b> - Calcula probabilidade do IP ser honeypot
/gp - Envia informações atuais do grupo
/ajuda - Envia a lista de comandos para ajuda
/info - Envia informações sobre o bot
/link - Envia link do grupo e do canal

<b>Apenas administrador ou moderador</b>
/k ou /kick - Remove o usuário alvo do grupo
/b ou /ban - Bane o usuário alvo do grupo
/titulo - Altera o título do grupo
/desc - Altera a descrição do grupo
"""

	bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=ajuda, reply_to_message_id=update.message.message_id)

def expulsar(bot, update):
	#expulsar alvo do grupo
	admin_list = bot.get_chat_administrators(chat_id=update.message.chat_id)
	user_id = update.message.from_user.id

	if check_adm(user_id=user_id, admin_list=admin_list) == True:
		alvo_id = update.message.reply_to_message.from_user.id
		alvo_usuario = update.message.reply_to_message.from_user.username
		alvo_nome = update.message.reply_to_message.from_user.first_name

		if alvo_usuario == None:
			expulso = '<b>Usuário {} - {} removido.</b>'.format(alvo_nome, alvo_id)
		else:
			expulso = '<b>Usuário {} - {} removido.</b>'.format(alvo_usuario, alvo_id)

		bot.kick_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
		bot.unban_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=expulso, reply_to_message_id=update.message.message_id)
	else:
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Você não é administrador para usar este comando.</b>', reply_to_message_id=update.message.message_id)

def banir(bot, update):
	#banir alvo do grupo
	admin_list = bot.get_chat_administrators(chat_id=update.message.chat_id)
	user_id = update.message.from_user.id

	if check_adm(user_id=user_id, admin_list=admin_list) == True:
		alvo_id = update.message.reply_to_message.from_user.id
		alvo_usuario = update.message.reply_to_message.from_user.username
		alvo_nome = update.message.reply_to_message.from_user.first_name

		if alvo_usuario == None:
			banido = '<b>Usuário {} - {} banido.</b>'.format(alvo_nome, alvo_id)
		else:
			banido = '<b>Usuário {} - {} banido.</b>'.format(alvo_usuario, alvo_id)

		bot.kick_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=banido, reply_to_message_id=update.message.message_id)
	else:
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Você não é administrador para usar este comando.</b>', reply_to_message_id=update.message.message_id)

def pin(bot, update):
	#fixar mensagem
	admin_list = bot.get_chat_administrators(chat_id=update.message.chat_id)
	user_id = update.message.from_user.id

	if check_adm(user_id=user_id, admin_list=admin_list) == True:
		bot.pin_chat_message(chat_id=update.message.chat_id, message_id=update.message.reply_to_message.message_id)
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Mensagem fixada.</b>', reply_to_message_id=update.message.reply_to_message.message_id)
	else:
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Você não é administrador para usar este comando.</b>', reply_to_message_id=update.message.message_id)

def main():
	updater = Updater(token=API_TOKEN)
	dispatcher = updater.dispatcher

	dispatcher.add_handler(CommandHandler('regras', regras))
	dispatcher.add_handler(CommandHandler('ip', ip, pass_args=True))
	dispatcher.add_handler(CommandHandler('honeypot', honeypot, pass_args=True))
	dispatcher.add_handler(CommandHandler('link', link))
	dispatcher.add_handler(CommandHandler('gp', gp))
	dispatcher.add_handler(CommandHandler('admin', admin))
	dispatcher.add_handler(CommandHandler('help', ajuda))
	dispatcher.add_handler(CommandHandler('info', info))
	dispatcher.add_handler(CommandHandler('kick', expulsar))
	dispatcher.add_handler(CommandHandler('k', expulsar))
	dispatcher.add_handler(CommandHandler('ban', banir))
	dispatcher.add_handler(CommandHandler('b', banir))
	dispatcher.add_handler(CommandHandler('pin', pin))

	# mensagem de boas vindas
	dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, bvindas))
	rodar(updater)

if __name__ == '__main__':
	main()
