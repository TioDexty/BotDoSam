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
import shutil
from nudity import Nudity
from PIL import Image
import Algorithmia

nudity = Nudity()

#BOT TOKEN
API_TOKEN = os.getenv('TOKEN')

#GRUPO_PERMITIDO (APENAS UM GRUPO)
OFC_G = os.getenv('ONE_GROUP_ONLY')

#REGISTRY_GROUP
REG_GROUP = os.getenv('REGISTER')

#MODO = DEV / PROD
modo = os.getenv('MODO')

#ALGORITHMIA NUDITY DETECTION
ALGORITHMIA_KEY = os.getenv('ALGO_KEY')
client = Algorithmia.client(ALGORITHMIA_KEY)
algo = client.algo('sfw/NudityDetection/1.1.6')
algo.set_options(timeout=300)

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
Excecoes = ['']

ids = open('ids.txt', 'r')
for i in ids:
	Excecoes.append(str(i))

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
		updater.bot.set_webhook('https://{}.herokuapp.com/{}'.format(HEROKU_NOME, API_TOKEN))
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

@run_async
def check_nude_sticker(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		'''
		A função check_nude_sticker será a versão 1.0 (sem Algorithmia), pois
		não é possível fazer a verificação com a extensão .webp.
		'''
		try:
			sticker = str(bot.get_file(update.message.sticker.file_id)).replace("'", '"')

			js = json.loads(sticker)
			sticker = js['file_path']

			r = requests.get(sticker, stream=True)
			sticker = sticker.split('/')[-1]

			with open(sticker, 'wb') as fo:
				shutil.copyfileobj(r.raw, fo)
			del r

			#transformando de webp para jpg
			im = Image.open(sticker).convert('RGB') 
			sticker = sticker.split('.')[0] + '.jpg'
			im.save(sticker, 'jpeg')

			if nudity.has(str(sticker)) == True: #checando se tem nude ou n com nudepy
				alvo_id = update.message.from_user.id
				alvo_usuario = update.message.from_user.username
				alvo_nome = update.message.from_user.first_name

				if str(alvo_id) not in Excecoes:
					if alvo_usuario == None:
						banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_nome, alvo_id)
					else:
						banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_usuario, alvo_id)

					banido_usuario = '''
#BANIDO_USUARIO
<b>Usuário: </b>{user_name} [<a href="{link}">{user_id}</a>]
<b>Grupo: </b>{group_name} [{group_id}]
<b>Data: </b>{data}
<b>Motivo: </b>{motivo}
'''.format(user_name=alvo_usuario,
					user_id=alvo_id,
					group_name=update.message.chat.title,
					group_id=update.message.chat.id,
					data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'),
					motivo='Pornografia',
					link='tg://user?id=' + str(alvo_id))

					bot.kick_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=banido, reply_to_message_id=update.message.message_id)
					bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
					bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=banido_usuario)

					del banido_usuario
					del banido
					del alvo_id
					del alvo_usuario
					del alvo_nome
			else: pass

			os.remove(sticker) #remove os stickers salvos para n ocupar espaço
			os.remove(sticker.split('.')[0] + '.webp') #remove os stickers salvos para n ocupar espaço
		
			del sticker
		except BadRequest as e:
			try:
				os.remove(sticker)
				os.remove(sticker.split('.')[0] + '.webp')
			except: pass

			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>O usuário é administrador e não pode ser banido.</b>', reply_to_message_id=update.message.message_id)
			bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

@run_async
def check_nude_image(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		try:
			foto = bot.get_file(update.message.photo[-1].file_id)

			foto = str(foto) #transformando o tipo type para string
			foto = foto.replace("'", '"') #substituindo os ' por "

			js = json.loads(foto) #carregando o json
			foto = js['file_path'] #conseguindo a fonte da imagem

			algo_js = algo.pipe(foto).result #passando a fonte na API do algorithmia

			if algo_js['nude'] == 'true': #checando se tem nude ou n
				alvo_id = update.message.from_user.id
				alvo_usuario = update.message.from_user.username
				alvo_nome = update.message.from_user.first_name

				if str(alvo_id) not in Excecoes:
					if alvo_usuario == None:
						banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_nome, alvo_id)
					else:
						banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_usuario, alvo_id)

					banido_usuario = '''
#BANIDO_USUARIO
<b>Usuário: </b>{user_name} [<a href="{link}">{user_id}</a>]
<b>Grupo: </b>{group_name} [{group_id}]
<b>Data: </b>{data}
<b>Motivo: </b>{motivo}
'''.format(user_name=alvo_usuario,
					user_id=alvo_id,
					group_name=update.message.chat.title,
					group_id=update.message.chat.id,
					data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'),
					motivo='Pornografia',
					link='tg://user?id=' + str(alvo_id))

					bot.kick_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=banido, reply_to_message_id=update.message.message_id)
					bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
					bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=banido_usuario)

					del banido_usuario
					del banido
					del alvo_id
					del alvo_usuario
					del alvo_nome
			else: pass

			#tentando liberar memória pro bot n explodir
			del js
			del algo_js

		except BadRequest as e:
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>O usuário é administrador e não pode ser banido.</b>', reply_to_message_id=update.message.message_id)
			bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

@run_async
def saida(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		m = update.message.left_chat_member

		if m is not None:
			if m.is_bot == True:
				bot_out = '''
#SAIDA_BOT
<b>De:</b> {bot_name} [<a href="{link}">{bot_id}</a>]
<b>Grupo:</b> {group_name} [{group_id}]
<b>Data:</b> {data}
'''.format(bot_name=m.full_name,
			bot_id=m.id,
			group_name=update.message.chat.title,
			group_id=update.message.chat.id,
			data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'),
			link='tg://user?id=' + str(m.id))

				bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=bot_out)
			else:
				user_out = '''
#SAIDA_USUARIO
<b>De:</b> {user_name} [<a href="{link}">{user_id}</a>]
<b>Grupo:</b> {group_name} [{group_id}]
<b>Data:</b> {data}
'''.format(user_name=m.full_name,
				user_id=m.id,
				group_name=update.message.chat.title,
				group_id=update.message.chat.id,
				data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'),
							link='tg://user?id=' + str(m.id))

				bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=user_out)

@run_async
def bvindas(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		for m in update.message.new_chat_members:
			alvo_id = m.id

			if m.full_name == None or m.first_name == None:
				m.full_name = m.username

			if m.is_bot == True:
				if str(alvo_id) not in Excecoes:
					bot.kick_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Bot {} removido.</b>'.format(alvo_id))

					bot_entry = '''
#ENTRADA_BOT
<b>De:</b> {bot_name} [<a href="{link}">{bot_id}</a>]
<b>Grupo:</b> {group_name} [{group_id}]
<b>Data:</b> {data}
'''.format(bot_name=m.full_name,
			bot_id=m.id,
			group_name=update.message.chat.title,
			group_id=update.message.chat.id,
			data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'),
						link='tg://user?id=' + str(m.id))

					bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=bot_entry)
				else: pass
			else:
				boasvindas = '<b>Olá, {}. Bem-vindo(a) ao {}.</b>'.format(m.full_name, update.message.chat.title)
				bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=boasvindas)

				user_entry = '''
#ENTRADA_USUARIO
<b>De:</b> {user_name} [<a href="{link}">{user_id}</a>]
<b>Grupo:</b> {group_name} [{group_id}]
<b>Data:</b> {data}
'''.format(user_name=m.full_name,
			user_id=m.id,
			group_name=update.message.chat.title,
			group_id=update.message.chat.id,
			data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'),
						link='tg://user?id=' + str(m.id))

				bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=user_entry)

def info(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		info_txt = """
<b>Olá, sou o bot do Sam, fui criado para administrar o canal e o grupo do @SamMarx.</b>

<b>Desenvolvedor: </b> <a href="http://t.me/SamMarx">Sam</a>.
<b>Código: </b> <a href="http://github.com/Sam-Marx/BotDoSam">Github</a>.
"""

		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=info_txt, reply_to_message_id=update.message.message_id)

def admin(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		try:
			msg = '<b>Administrador(es)</b>\n\n'

			for adm in bot.get_chat_administrators(chat_id=update.message.chat_id):
				adm_username = adm.user

				msg += '<b>@{username}</b>\n'.format(username=adm_username['username'])

			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=msg, reply_to_message_id=update.message.message_id)
		except BadRequest as e:
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Erro: </b>{}'.format(e), reply_to_message_id=update.message.message_id)

def link(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
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
	if check_group(chat_id=update.message.chat_id) == True:
		msg = """
<b>Informações atuais do grupo</b>

<b>Título:</b> {}
<b>Número de membros:</b> {}
""".format(update.message.chat.title, bot.get_chat_members_count(chat_id=update.message.chat_id))

		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=msg, reply_to_message_id=update.message.message_id)
	else:
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=str(update.message.chat_id), reply_to_message_id=update.message.message_id)

def excecoes(bot, update, args):
	admin_list = bot.get_chat_administrators(chat_id=update.message.chat_id)
	user_id = update.message.from_user.id

	if check_adm(user_id=user_id, admin_list=admin_list) == True:
		try:
			ids_txt = open('ids.txt', 'r+').readlines()

			for tg_id in ids_txt:
				if str(tg_id) == str(args[0]):
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>O ID {} já é uma exceção.</b>'.format(args[0]), reply_to_message_id=update.message.message_id)
				else:
					ids_txt.write('\n' + str(args[0]))
					bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>O ID {} agora é uma exceção e pode ser adicionado ao grupo.</b>'.format(args[0]), reply_to_message_id=update.message.message_id)
		
			ids_txt.close()
		except Exception as e:
			print('Erro: ' + str(e))
	else:
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Você não é administrador para usar este comando.</b>', reply_to_message_id=update.message.message_id)

def honeypot(bot, update, args):
	if check_group(chat_id=update.message.chat_id) == True:
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
	if check_group(chat_id=update.message.chat_id) == True:
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
	if check_group(chat_id=update.message.chat_id) == True:
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
<b>10.</b> Não envie links suspeitos nem links de grupos/canais do Telegram, apenas com autorização de um administrador.
"""
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=regras, reply_to_message_id=update.message.message_id)

def ajuda(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		ajuda = """
/ip <b>IP</b> - Mostra informações sobre o endereço IP
/regras - Envia a lista de regras do grupo
/honeypot <b>IP</b> - Calcula probabilidade do IP ser honeypot
/gp - Envia informações atuais do grupo
/ajuda - Envia a lista de comandos para ajuda
/info - Envia informações sobre o bot
/link - Envia link do grupo e do canal
/s ou /salvar - Envia a mensagem escolhida para o seu pv
/rk ou /requestkick - Pede expulsão de um usuário
/rb ou /requestban - Pede banimento de um usuário

<b>Apenas administrador ou moderador</b>
/k ou /kick - Remove o usuário alvo do grupo
/b ou /ban - Bane o usuário alvo do grupo
/p ou /pin - Fixa uma mensagem escolhida
/unban <b>ID</>/<b>mensagem do banido</b> - Desbane um usuário
/exc <b>ID</b> - Adiciona ID de um bot como exceção
"""

		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=ajuda, reply_to_message_id=update.message.message_id)

def expulsar(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
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

def desbanir(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		admin_list = bot.get_chat_administrators(chat_id=update.message.chat_id)
		user_id = update.message.from_user.id

		if check_adm(user_id=user_id, admin_list=admin_list) == True:
			try:
				alvo_id = update.message.reply_to_message.from_user.id
				alvo_usuario = update.message.reply_to_message.from_user.username
				alvo_nome = update.message.reply_to_message.from_user.first_name

				user_desban = '''
#DESBAN_USUARIO
<b>Usuário:</b> {user_name} [{user_id}]
<b>Grupo:</b> {group_name} [{group_id}]
<b>Data:</b> {data}
'''.format(user_name=alvo_usuario,
			user_id=alvo_id,
			group_name=update.message.chat.title,
			group_id=update.message.chat.id,
			data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'))

				bot.unban_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
				bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Usuário {} - {} desbanido.</b>'.format(alvo_usuario, alvo_id), reply_to_message_id=update.message.message_id)
				bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=user_desban)
			except IndexError:
				pass

def banir(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
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

def pedir_ban(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		#pedir ban do alvo
		pedinte = update.message.from_user
		baninte = update.message.reply_to_message.from_user

		mensagem = '''
<b>O usuário {a} está pedindo banimento do usuário {b}.</b>

<b>Mais informações</b>
<b>ID: </b>{a_id}
<b>Nome: </b>{a_full_name}
<b>Nome de usuário: </b>{a_username}

<b>Usuário a ser banido</b>
<b>ID: </b>{b_id}
<b>Nome: </b>{b_full_name}
<b>Nome de usuário: </b>{b_username}

<a href="{link}">Link para a mensagem</a>
'''.format(a=pedinte.full_name,
		b=baninte.full_name,
		a_id=pedinte.id,
		a_full_name=pedinte.full_name,
		a_username=pedinte.username,

		b_id=baninte.id,
		b_full_name=baninte.full_name,
		b_username=baninte.username,
		link=update.message.link)

		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Chamando os administradores, aguarde.</b>', reply_to_message_id=update.message.message_id)

		for admin in bot.get_chat_administrators(chat_id=update.message.chat_id):
			bot.send_message(parse_mode='HTML', chat_id=admin.user.id, text=mensagem)

def pedir_kick(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		#pedir ban do alvo
		pedinte = update.message.from_user
		kickinte = update.message.reply_to_message.from_user

		mensagem = '''
<b>O usuário {a} está pedindo expulsão do usuário {b}.</b>

<b>Mais informações</b>
<b>ID: </b>{a_id}
<b>Nome: </b>{a_full_name}
<b>Nome de usuário: </b>{a_username}

<b>Usuário a ser banido</b>
<b>ID: </b>{b_id}
<b>Nome: </b>{b_full_name}
<b>Nome de usuário: </b>{b_username}

<a href="{link}">Link para a mensagem</a>
'''.format(a=pedinte.full_name,
		b=kickinte.full_name,
		a_id=pedinte.id,
		a_full_name=pedinte.full_name,
		a_username=pedinte.username,

		b_id=kickinte.id,
		b_full_name=kickinte.full_name,
		b_username=kickinte.username,
		link=update.message.link)

		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Chamando os administradores, aguarde.</b>', reply_to_message_id=update.message.message_id)

		for admin in bot.get_chat_administrators(chat_id=update.message.chat_id):
			bot.send_message(parse_mode='HTML', chat_id=admin.user.id, text=mensagem)

def pin(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		#fixar mensagem
		admin_list = bot.get_chat_administrators(chat_id=update.message.chat_id)
		user_id = update.message.from_user.id

		if check_adm(user_id=user_id, admin_list=admin_list) == True:
			bot.pin_chat_message(chat_id=update.message.chat_id, message_id=update.message.reply_to_message.message_id)
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Mensagem fixada.</b>', reply_to_message_id=update.message.reply_to_message.message_id)
		else:
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Você não é administrador para usar este comando.</b>', reply_to_message_id=update.message.message_id)

def salvar(bot, update):
	if check_group(chat_id=update.message.chat_id) == True:
		#salvar mensagem
		user_link = update.message.from_user.link
		user_id = update.message.from_user.id

		bot.forward_message(chat_id=user_id, from_chat_id=update.message.chat_id, message_id=update.message.reply_to_message.message_id)
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>A mensagem foi salva no seu privado.</b>', reply_to_message_id=update.message.message_id)

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
	dispatcher.add_handler(CommandHandler('p', pin))
	dispatcher.add_handler(CommandHandler('salvar', salvar))
	dispatcher.add_handler(CommandHandler('s', salvar))
	dispatcher.add_handler(CommandHandler('unban', desbanir))
	dispatcher.add_handler(CommandHandler('requestban', pedir_ban))
	dispatcher.add_handler(CommandHandler('rb', pedir_ban))
	dispatcher.add_handler(CommandHandler('requestkick', pedir_kick))
	dispatcher.add_handler(CommandHandler('rk', pedir_kick))
	dispatcher.add_handler(CommandHandler('exc', excecoes, pass_args=True))

	# mensagem de boas vindas
	dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, bvindas))

	# saida
	dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, saida))
	
	# filtrar imagens
	dispatcher.add_handler(MessageHandler(Filters.photo, check_nude_image))

	# filtrar stickers
	dispatcher.add_handler(MessageHandler(Filters.sticker, check_nude_sticker))
	
	rodar(updater)

if __name__ == '__main__':
	main()
