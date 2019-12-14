#coding: utf-8
#!/usr/bin/python3.7
#Bot do Sam
#@AcervoDoSam
#@GrupoDoSam

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.error import NetworkError, Unauthorized, BadRequest
import logging
import requests
import json
import shodan
import random
import sys
import os
import re
import datetime
import socket
from pytz import timezone
import unicodedata as ud

#BOT TOKEN
API_TOKEN = os.getenv('TOKEN')

#GRUPO_PERMITIDO (APENAS UM GRUPO)
OFC_G = os.getenv('ONE_GROUP_ONLY')

#REGISTRY_GROUP
REG_GROUP = os.getenv('REGISTER')

#MODO = DEV / PROD
modo = os.getenv('MODO')

#SHODAN KEYS
shod_key1 = os.getenv('SHODAN_1')
shod_key2 = os.getenv('SHODAN_2')
shodan_keys = ['']
shodan_keys.append(shod_key1)
shodan_keys.append(shod_key2)

####
canal = ['https://t.me/AcervoDoSam', '@AcervoDoSam']
####

permitidos = ['-1001480767444']

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
			url_path=API_TOKEN)
		updater.bot.set_webhook(f'https://{HEROKU_NOME}.herokuapp.com/{API_TOKEN}')
else:
	logging.error('MODO NÃO ESPECIFICADO')
	sys.exit()

def check_group(chat_id):
	if str(chat_id) == str(OFC_G):
		return True
	else:
		return False

def check_adm(user_id, admin_list):
	for adm in admin_list:
		adm_id = adm.user.id
		if adm_id == user_id:
			return True
	return False

def check_arabe(nome):
	for l in nome:
		try:
			enc = ud.name(l).lower()
			if 'arabic' in enc or 'persian' in enc:
				return True
		except Exception:
			pass
	return False

def check_indiano(nome):
	for l in nome:
		try:
			enc = ud.name(l).lower()
			if 'devanagari' in enc:
				return True
		except Exception:
			pass
	return False

@run_async
def saida(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		m = update.message.left_chat_member
		ids_txt = open('ids.txt', 'r+')

		if m is not None:
			if m.is_bot == True: pass
			else:
				data = datetime.datetime.now(timezone("America/Sao_Paulo")).strftime("%H:%M %d %B, %Y")
				user_out = f'''
#SAIDA_USUARIO
<b>De:</b> {user_name} [<a href="tg://user?id={str(m.id)}">{m.id}</a>]
<b>Grupo:</b> {update.message.chat.title} [{update.message.chat.id}]
<b>Data:</b> {data}'''

				bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=user_out)

@run_async
def bvindas(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		for m in update.message.new_chat_members:
			ids_txt = open('ids.txt', 'r+')

			if m.full_name == None or m.first_name == None:
				if m.username != None:
					m.full_name = m.username
				else:
					bot.kick_chat_member(chat_id=update.message.chat_id, user_id=m.id)

			if m.is_bot == True:
				if str(m.id) not in ids_txt.readlines():
					bot.kick_chat_member(chat_id=update.message.chat_id, user_id=m.id)
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=f'<b>Bot {m.id} removido.</b>')
					data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y')
					bot_entry = f'''
#ENTRADA_BOT
<b>De:</b> {m.full_name} [<a href="tg://user?id={str(m.id)}">{m.id}</a>]
<b>Grupo:</b> {update.message.chat.title} [{update.message.chat.id}]
<b>Data:</b> {data}
'''

					bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=bot_entry)
				else: pass
			elif check_arabe(m.full_name):
				if str(m.id) not in ids_txt.readlines():
					bot.kick_chat_member(chat_id=update.message.chat_id, user_id=m.id)
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=f'<b>Árabe {m.full_name} banido.</b>')
					data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y')
					bot_entry = f'''
#ENTRADA_ARABE
<b>De:</b> {m.full_name} [<a href="tg://user?id={str(m.id)}">{m.id}</a>]
<b>Grupo:</b> {update.message.chat.title} [{update.message.chat.id}]
<b>Data:</b> {data}
<b>Situação:</b> banido por ser árabe
'''

					bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=bot_entry)

			elif check_indiano(m.full_name):
				if str(m.id) not in ids_txt.readlines():
					bot.kick_chat_member(chat_id=update.message.chat_id, user_id=m.id)
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=f'<b>Indiano {m.full_name} banido.</b>')

					bot_entry = f'''
#ENTRADA_INDIANO
<b>De:</b> {m.full_name} [<a href="tg://user?id={str(m.id)}">{m.id}</a>]
<b>Grupo:</b> {update.message.chat.title} [{update.message.chat.id}]
<b>Data:</b> {data}
<b>Situação:</b> banido por ser indiano
'''

					bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=bot_entry)

			else:
				boasvindas = '<b>Olá, {m.full_name}. Bem-vindo(a) ao {update.message.chat.title}.</b>'
				bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=boasvindas)
				data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y')
				user_entry = f'''
#ENTRADA_USUARIO
<b>De:</b> {m.full_name} [<a href="tg://user?id={str(m.id)}">{m.id}</a>]
<b>Grupo:</b> {update.message.chat.title} [{update.message.chat.id}]
<b>Data:</b> {data}
'''

				bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=user_entry)

def info(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		info_txt = """
<b>Olá, sou o bot do Sam, fui criado para administrar o grupo de @SamMarx.</b>

<b>Desenvolvedor: </b> <a href="http://t.me/SamMarx">Sam</a>.
<b>Código: </b> <a href="http://github.com/Sam-Marx/BotDoSam">Github</a>.
"""

		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=info_txt, reply_to_message_id=update.message.message_id)

def link(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		cnl = random.choice(canal)

		try:
			msg = f"""
<b>Link do grupo: </b>{bot.export_chat_invite_link(chat_id=update.message.chat_id)}
<b>Link do canal: </b>{cnl}
	"""
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=msg, reply_to_message_id=update.message.message_id)
		except BadRequest as e:
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=f'<b>Erro: </b>{e}\n\nTalvez eu precise de permissões de administrador para executar este comando.', reply_to_message_id=update.message.message_id)

def gp(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		msg = f"""
<b>Informações atuais do grupo</b>

<b>Título:</b> {update.message.chat.title}
<b>Número de membros:</b> {bot.get_chat_members_count(chat_id=update.message.chat_id)}
"""
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=msg, reply_to_message_id=update.message.message_id)
	else:
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=str(update.message.chat_id), reply_to_message_id=update.message.message_id)

def excecoes(bot, update, args):
	if check_adm(user_id=update.message.from_user.id, admin_list=bot.get_chat_administrators(chat_id=update.message.chat_id)) == True:
		try:
			ids_txt = open('ids.txt', 'r+')

			for tg_id in ids_txt.readlines():
				if str(tg_id) == str(args[0]):
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=f'<b>O ID {args[0]} já é uma exceção.</b>', reply_to_message_id=update.message.message_id)
					break
				else:
					ids_txt.write('\n' + str(args[0]))
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=f'<b>O ID {args[0]} agora é uma exceção e pode ser adicionado ao grupo.</b>', reply_to_message_id=update.message.message_id)
				break

			ids_txt.close()
		except Exception as e:
			pass
	else:
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Você não é administrador para usar este comando.</b>', reply_to_message_id=update.message.message_id)

def ip(bot, update, args):
	if check_group(chat_id=update.message.chat_id) == True:
		try:
			args[0] = socket.gethostbyname(args[0])

			key = random.choice(shodan_keys)

			api = shodan.Shodan(key)

			ip_text = f"""
<b>IP: </b>{args[0]} sendo escaneado.

Voltarei com os resultados assim que possível."""

			msg = bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=ip_text, reply_to_message_id=update.message.message_id)

			try:
				geo_ip = requests.get(f'http://ip-api.com/json/{args[0]}')

				geo_ip_json = json.loads(geo_ip.text)

				asn = geo_ip_json['as']
				cidade = geo_ip_json['city']
				pais =geo_ip_json['country']
				codigoPais = geo_ip_json['countryCode']
				isp = geo_ip_json['isp']
				lat = geo_ip_json['lat']
				lon = geo_ip_json['lon']

				host = api.host(args[0])
				org = host.get('org', 'n/a')
				os = host.get('os', 'n/a')
				ports = host.get('ports', 'n/a')

				novo_texto = f"""
<b>IP: </b>{args[0]}
<b>Hospedado por: </b>{asn}
<b>País: </b>{pais} - {codigoPais}
<b>Cidade: </b>{cidade}
<b>ISP: </b>{isp}
<b>Latitude: </b>{lat}
<b>Longitude: </b>{lon}

<b>Organização: </b>{org}
<b>Sistema operacional: </b>{os}
<b>Portas: </b>{ports}
"""	

				bot.edit_message_text(parse_mode='HTML', chat_id=update.message.chat_id, 
					message_id=msg.message_id, 
					text=novo_texto)

			except shodan.APIError as e:
				err_t = f"<b>Erro com o IP {args[0]}: </b>{e}"
				bot.edit_message_text(parse_mode='HTML', chat_id=update.message.chat_id, message_id=msg.message_id, text=err_t)

			except BadRequest as e:
				err_t = f"<b>Erro: </b>{e}\n\nTente novamente mais tarde."
				bot.edit_message_text(parse_mode='HTML', chat_id=update.message.chat_id, message_id=msg.message_id, text=err_t)

			except Exception as e:
				pass

		except IndexError:
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='/ip <b>IP</b>/<b>DOMÍNIO</b> para obter informações sobre o endereço.', reply_to_message_id=update.message.message_id)

def regras(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		regras = """
<b>Leis:</b>

<b>1.</b> Não envie ou peça qualquer tipo de pornografia;
<b>2.</b> Não envie ou peça qualquer tipo de conteúdo extremo, seja ele "gore", "scat" ou outro;
<b>3.</b> Não envie ou peça qualquer tipo de informação pessoal ("dox"/"exposed");
<b>4.</b> Se você tem alguma sugestão, envie-a no grupo;
<b>5.</b> Não cometa flood, não envie muitas mensagens pequenas, não abuse de GIFs, "stickers" nem emojis;
<b>6.</b> Não compartilhe nenhum APK ou executável sem sua "hash" ou seu link de verificação do "VirusTotal";
<b>7.</b> Não espere atenção 24/7 do administrador ou moderador;
<b>8.</b> Não seja analfabeto nem mesmo funcional;
<b>9.</b> Não envie links suspeitos nem links de grupos/canais do Telegram, apenas com autorização de um administrador; e
<b>10.</b> Não peça cartões clonados, bins, checkers etc.
"""
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=regras, reply_to_message_id=update.message.message_id)

def ajuda(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		ajuda = """
/ip <b>IP</b> - Mostra informações sobre o endereço IP
/leis - Envia a lista de leis do grupo
/gp - Envia informações atuais do grupo
/ajuda - Envia a lista de comandos para ajuda
/info - Envia informações sobre o bot
/link - Envia link do grupo e do canal
/s ou /salvar - Envia a mensagem escolhida para o seu pv

<b>Apenas administrador ou moderador</b>
/k ou /kick - Remove o usuário alvo do grupo
/b ou /ban - Bane o usuário alvo do grupo
/p ou /pin - Fixa uma mensagem escolhida
/unban <b>ID</>/<b>mensagem do banido</b> - Desbane um usuário
/exc <b>ID</b> - Adiciona ID de um bot como exceção
/m ou /mute - Deixa o usuário mudo, incapaz de mandar mensagens
/unmute - Permite que o usuário fale
"""

		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=ajuda, reply_to_message_id=update.message.message_id)

def expulsar(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		#expulsar alvo do grupo
		if check_adm(user_id=update.message.from_user.id, admin_list=bot.get_chat_administrators(chat_id=update.message.chat_id)) == True:
			if alvo_usuario == None:
				expulso = f'<b>Usuário {update.message.reply_to_message.from_user.first_name} - {update.message.reply_to_message.from_user.id} removido.</b>'
			else:
				expulso = f'<b>Usuário {update.message.reply_to_message.from_user.username} - {update.message.reply_to_message.from_user.id} removido.</b>'

			bot.kick_chat_member(chat_id=update.message.chat_id, user_id=update.message.reply_to_message.from_user.id)
			bot.unban_chat_member(chat_id=update.message.chat_id, user_id=update.message.reply_to_message.from_user.id)
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=expulso, reply_to_message_id=update.message.message_id)
		else:
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Você não é administrador para usar este comando.</b>', reply_to_message_id=update.message.message_id)

def desbanir(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		if check_adm(user_id=update.message.from_user.id, admin_list=bot.get_chat_administrators(chat_id=update.message.chat_id)) == True:
			try:
				data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y')
				user_desban = f'''
#DESBAN_USUARIO
<b>Usuário:</b> {update.message.reply_to_message.from_user.username} [{update.message.reply_to_message.from_user.id}]
<b>Grupo:</b> {update.message.chat.title} [{update.message.chat.id}]
<b>Data:</b> {data}
'''
				bot.unban_chat_member(chat_id=update.message.chat_id, user_id=update.message.reply_to_message.from_user.id)
				bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Usuário {update.message.reply_to_message.from_user.username} - {update.message.reply_to_message.from_user.id} desbanido.</b>', reply_to_message_id=update.message.message_id)
				bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=user_desban)
			except IndexError:
				pass

def banir(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		#banir alvo do grupo
		if check_adm(user_id=update.message.from_user.id, admin_list=bot.get_chat_administrators(chat_id=update.message.chat_id)) == True:
			if alvo_usuario == None:
				banido = f'<b>Usuário {update.message.reply_to_message.from_user.first_name} - {update.message.reply_to_message.from_user.id} banido.</b>'
			else:
				banido = f'<b>Usuário {update.message.reply_to_message.from_user.username} - {update.message.reply_to_message.from_user.id} banido.</b>'

			bot.kick_chat_member(chat_id=update.message.chat_id, user_id=update.message.reply_to_message.from_user.id)
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=banido, reply_to_message_id=update.message.message_id)
		else:
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Você não é administrador para usar este comando.</b>', reply_to_message_id=update.message.message_id)

def mute(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		#mutar usuario
		if check_adm(user_id=update.message.from_user.id, admin_list=bot.get_chat_administrators(chat_id=update.message.chat_id)) == True:
			if alvo_usuario == None:
				mudo = f'<b>Usuário {update.message.reply_to_message.from_user.first_name} - {update.message.reply_to_message.from_user.id} agora está mudo.</b>'
			else:
				mudo = f'<b>Usuário {pdate.message.reply_to_message.from_user.username} - {update.message.reply_to_message.from_user.id} agora está mudo.</b>'

			bot.restrict_chat_member(chat_id=update.message.chat_id, user_id=update.message.reply_to_message.from_user.id, can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=mudo, reply_to_message_id=update.message.message_id)
		else:
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Você não é administrador para usar este comando.</b>', reply_to_message_id=update.message.message_id)

def unmute(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		#mutar usuario
		if check_adm(user_id=update.message.from_user.id, admin_list=bot.get_chat_administrators(chat_id=update.message.chat_id)) == True:
			if alvo_usuario == None:
				mudo = f'<b>Usuário {update.message.reply_to_message.from_user.first_name} - {update.message.reply_to_message.from_user.id} não está mais mudo.</b>'
			else:
				mudo = f'<b>Usuário {update.message.reply_to_message.from_user.username} - {update.message.reply_to_message.from_user.id} não está mais mudo.</b>'

			bot.restrict_chat_member(chat_id=update.message.chat_id, user_id=update.message.reply_to_message.from_user.id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=mudo, reply_to_message_id=update.message.message_id)
		else:
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Você não é administrador para usar este comando.</b>', reply_to_message_id=update.message.message_id)

def pin(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		#fixar mensagem
		if check_adm(user_id=update.message.from_user.id, admin_list=bot.get_chat_administrators(chat_id=update.message.chat_id)) == True:
			bot.pin_chat_message(chat_id=update.message.chat_id, message_id=update.message.reply_to_message.message_id)
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Mensagem fixada.</b>', reply_to_message_id=update.message.reply_to_message.message_id)
		else:
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Você não é administrador para usar este comando.</b>', reply_to_message_id=update.message.message_id)

def salvar(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		#salvar mensagem
		bot.forward_message(chat_id=update.message.from_user.id, from_chat_id=update.message.chat_id, message_id=update.message.reply_to_message.message_id)
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>A mensagem foi salva no seu privado.</b>', reply_to_message_id=update.message.message_id)

def main():
	updater = Updater(token=API_TOKEN)
	dispatcher = updater.dispatcher

	dispatcher.add_handler(CommandHandler('leis', regras))
	dispatcher.add_handler(CommandHandler('ip', ip, pass_args=True))
	dispatcher.add_handler(CommandHandler('link', link))
	dispatcher.add_handler(CommandHandler('gp', gp))
	dispatcher.add_handler(CommandHandler('help', ajuda))
	dispatcher.add_handler(CommandHandler('info', info))
	dispatcher.add_handler(CommandHandler('kick', expulsar))
	dispatcher.add_handler(CommandHandler('k', expulsar))
	dispatcher.add_handler(CommandHandler('ban', banir))
	dispatcher.add_handler(CommandHandler('b', banir))
	dispatcher.add_handler(CommandHandler('pin', pin))
	dispatcher.add_handler(CommandHandler('p', pin))
	dispatcher.add_handler(CommandHandler('salvar', salvar))
	dispatcher.add_handler(CommandHandler('s', salvar))
	dispatcher.add_handler(CommandHandler('unban', desbanir))
	dispatcher.add_handler(CommandHandler('exc', excecoes, pass_args=True))
	dispatcher.add_handler(CommandHandler('mute', mute))
	dispatcher.add_handler(CommandHandler('m', mute))
	dispatcher.add_handler(CommandHandler('unmute', unmute))

	# mensagem de boas vindas
	dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, bvindas))

	# saida
	dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, saida))
	rodar(updater)

if __name__ == '__main__':
	main()
