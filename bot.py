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
import nude
import shutil
from nude import Nude

API_TOKEN = os.getenv('TOKEN')

REG_GROUP = os.getenv('REGISTER')

modo = os.getenv('MODO')

shod_key1 = os.getenv('SHODAN_1')
shod_key2 = os.getenv('SHODAN_2')

shodan_keys = ['']

shodan_keys.append(shod_key1)
shodan_keys.append(shod_key2)

####
canal = ['https://t.me/AcervoDoSam', '@AcervoDoSam']
####

Excecoes = ['804801117'] #suporte

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

def check_adm(user_id, admin_list):
	for adm in admin_list:
		adm_id = adm.user.id
		if adm_id == user_id:
			return True
	return False

@run_async
def check_nude(bot, update):
	foto = bot.get_file(update.message.photo[-1].file_id)
	print(foto)

	r = requests.get(foto, stream=True)
	foto = foto.split('/')[-1]

	with open(foto, 'wb') as fo:
		shutil.copyfileobj(r.raw, fo)
	del r

	if nude.is_nude(str(foto)) == True:
		alvo_id = update.message.reply_to_message.from_user.id
		alvo_usuario = update.message.reply_to_message.from_user.username
		alvo_nome = update.message.reply_to_message.from_user.first_name

		if alvo_usuario == None:
			banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_nome, alvo_id)
		else:
			banido = '<b>Usuário {} - {} banido por envio de pornografia.</b>'.format(alvo_usuario, alvo_id)

		bot.kick_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=banido, reply_to_message_id=update.message.message_id)
	else: pass
@run_async
def saida(bot, update):
	m = update.message.left_chat_member

	if m is not None:
		if m.is_bot == True:
			bot_out = '''
#SAIDA_BOT
<b>De:</b> {bot_name} [{bot_id}]
<b>Grupo:</b> {group_name} [{group_id}]
<b>Data:</b> {data}
'''.format(bot_name=m.full_name,
		bot_id=m.id,
		group_name=update.message.chat.title,
		group_id=update.message.chat.id,
		data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'))

			bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=bot_out)
		else:
			user_out = '''
#SAIDA_USUARIO
<b>De:</b> {user_name} [{user_id}]
<b>Grupo:</b> {group_name} [{group_id}]
<b>Data:</b> {data}
'''.format(user_name=m.full_name,
			user_id=m.id,
			group_name=update.message.chat.title,
			group_id=update.message.chat.id,
			data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'))

			bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=user_out)

@run_async
def bvindas(bot, update):
	for m in update.message.new_chat_members:
		alvo_id = m.id

		if m.full_name == None or m.first_name == None:
			m.full_name = m.username

		if m.is_bot == True:
			if alvo_id not in Excecoes:
				bot.kick_chat_member(chat_id=update.message.chat_id, user_id=alvo_id)
				bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>Bot {} removido.</b>'.format(alvo_id))

				bot_entry = '''
#ENTRADA_BOT
<b>De:</b> {bot_name} [{bot_id}]
<b>Grupo:</b> {group_name} [{group_id}]
<b>Data:</b> {data}
'''.format(bot_name=m.full_name,
		bot_id=m.id,
		group_name=update.message.chat.title,
		group_id=update.message.chat.id,
		data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'))

				bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=bot_entry)
			else: pass
		else:
			boasvindas = '<b>Olá, {}. Bem-vindo(a) ao {}.</b>'.format(m.full_name, update.message.chat.title)
			bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=boasvindas)

			user_entry = '''
#ENTRADA_USUARIO
<b>De:</b> {user_name} [{user_id}]
<b>Grupo:</b> {group_name} [{group_id}]
<b>Data:</b> {data}
'''.format(user_name=m.full_name,
		user_id=m.id,
		group_name=update.message.chat.title,
		group_id=update.message.chat.id,
		data=datetime.datetime.now(timezone('America/Sao_Paulo')).strftime('%H:%M %d %B, %Y'))

			bot.send_message(parse_mode='HTML', chat_id=REG_GROUP, text=user_entry)

def info(bot, update):
	info_txt = """
<b>Olá, sou o bot do Sam, fui criado para administrar o canal e o grupo do @SamMarx.</b>

<b>Desenvolvedor: </b> <a href="http://t.me/SamMarx">Sam</a>.
<b>Código: </b> <a href="http://github.com/Sam-Marx/BotDoSam">Github</a>.
"""

	bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=info_txt, reply_to_message_id=update.message.message_id)

def admin(bot, update):
	try:
		msg = '<b>Administrador(es)</b>\n\n'

		for adm in bot.get_chat_administrators(chat_id=update.message.chat_id):
			adm_username = adm.user

			msg += '<b>@{username}</b>\n'.format(username=adm_username['username'])

		bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=msg, reply_to_message_id=update.message.message_id)
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
	msg = """
<b>Informações atuais do grupo</b>

<b>Título:</b> {}
<b>Número de membros:</b> {}
""".format(update.message.chat.title, bot.get_chat_members_count(chat_id=update.message.chat_id))

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
<b>10.</b> Não envie links suspeitos nem links de grupos/canais do Telegram, apenas com autorização de um administrador.
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
/emailrep - Recolhe informações básicas de um endereço de email
/s ou /salvar - Envia a mensagem escolhida para o seu pv

<b>Apenas administrador ou moderador</b>
/k ou /kick - Remove o usuário alvo do grupo
/b ou /ban - Bane o usuário alvo do grupo
/p ou /pin - Fixa uma mensagem escolhida
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

def salvar(bot, update):
	#salvar mensagem
	user_link = update.message.from_user.link
	user_id = update.message.from_user.id

	bot.forward_message(chat_id=user_id, from_chat_id=update.message.chat_id, message_id=update.message.reply_to_message.message_id)
	bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text='<b>A mensagem foi salva no seu privado.</b>', reply_to_message_id=update.message.message_id)

def emailrep(bot, update, args):
	#usa a API do emailrep para conseguir a reputação de um e-mail

	r = requests.get('https://emailrep.io/' + args[0])
	j = json.loads(r.text)

	carregando = '''
<b>Conseguindo reputação do e-mail </b>{} <b>.</b>

<b>Por favor, aguarde.</b>'''.format(args[0])

	msg = bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=carregando, reply_to_message_id=update.message.message_id)

	####

	emailrep_text = '''
<b>High</b> - Alta
<b>Medium</b> - Média
<b>Low</b> - Baixa
<b>None</b> - Nenhuma

<b>E-mail: </b>{email}
<b>Reputação: </b>{rep}
<b>Suspeitas: </b>{suspicious}
<b>Referências: </b>{references}

<b>Detalhes: </b>
	<b>Atividade maliciosa: </b>{activity}
	<b>Atividade maliciosa recente: </b>{recent_activity}
	<b>Credenciais vazadas: </b>{credentials}
	<b>Violação de dados: </b>{data_breach}
	<b>Visto pela última vez: </b>{last_seen}
	<b>Existe domínio: </b>{domain_exists}
	<b>Reputação de domínio: </b>{domain_rep}
	<b>Domínio novo: </b>{new_domain}
	<b>Dias desde criação de domínio: </b>{days}
	<b>TLD suspeito: </b>{suspicious_tld}
	<b>Spam: </b>{spam}
	<b>Provedor de graça: </b>{free_prov}
	<b>Descartável: </b>{disp}
	<b>MX válido: </b>{valid_mx}
	<b>Falsificável: </b>{spoofable}
	<b>SPF estrito: </b>{spf}
	<b>Dmarc reforçado: </b>{dmarc}

<b>Perfis:</b>
'''.format(email=args[0],
		rep=j['reputation'],
		suspicious=j['suspicious'],
		references=j['references'],
			activity=j['details']['malicious_activity'],
			recent_activity=j['details']['malicious_activity_recent'],
			credentials=j['details']['credentials_leaked'],
			data_breach=j['details']['data_breach'],
			last_seen=j['details']['last_seen'],
			domain_exists=j['details']['domain_exists'],
			domain_rep=j['details']['domain_reputation'],
			new_domain=j['details']['new_domain'],
			days=j['details']['days_since_domain_creation'],
			suspicious_tld=j['details']['suspicious_tld'],
			spam=j['details']['spam'],
			free_prov=j['details']['free_provider'],
			disp=j['details']['disposable'],
			valid_mx=j['details']['valid_mx'],
			spoofable=j['details']['spoofable'],
			spf=j['details']['spf_strict'],
			dmarc=j['details']['dmarc_enforced'])

	for perfil in j['details']['profiles']:
		emailrep_text += '<code>{}</code>\n'.format(perfil)

	bot.edit_message_text(parse_mode='HTML', chat_id=update.message.chat_id, message_id=msg.message_id, text=emailrep_text)

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
	dispatcher.add_handler(CommandHandler('emailrep', emailrep, pass_args=True))

	# mensagem de boas vindas
	dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, bvindas))

	# saida
	dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, saida))
	
	# filtrar imagens
	dispatcher.add_handler(MessageHandler(Filters.photo, check_nude))

	rodar(updater)

if __name__ == '__main__':
	main()
