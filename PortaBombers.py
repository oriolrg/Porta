#coder :- Oriol Riu

import os
import sys
import time
import telepot
import RPi.GPIO as GPIO
import time
from config.users import usuari, administradors

USERS_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'users.py')
ENV_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
ADMIN_HELP = """Comandes administrador:
Ajuda - mostra aquesta ajuda
Info - mostra quina copia del programa s'esta executant
Llista - llista usuaris i administradors
Nou:<codi>:<nom> - afegeix un usuari nou amb nom
Elimina:<codi> - elimina un usuari
Admin:<codi> - dona rol administrador
NoAdmin:<codi> - treu rol administrador"""

#Usuaris

# capto el token de la linea de comandos

def carregar_token():
    token = os.environ.get('TELEGRAM_TOKEN')
    if token:
        return token
    if os.path.exists(ENV_CONFIG):
        with open(ENV_CONFIG) as f:
            for linia in f:
                linia = linia.strip()
                if not linia or linia.startswith('#') or '=' not in linia:
                    continue
                clau, valor = linia.split('=', 1)
                if clau.strip() == 'TELEGRAM_TOKEN':
                    return valor.strip().strip('"').strip("'")
    raise RuntimeError("Falta TELEGRAM_TOKEN al fitxer .env")

TOKEN = carregar_token()
bot = telepot.Bot(TOKEN) #activo l'escolta del bot

# Configuracio per utilitzar Raspberry Pi board pin numbers
GPIO.setmode(GPIO.BOARD)
# Activo GPIO output channel
GPIO.setup(7, GPIO.OUT)

def es_admin(chat_id):
    return str(chat_id) in administradors

def guardar_configuracio():
    with open(USERS_CONFIG, 'w') as f:
        f.write('usuari = {\n')
        for user_id, nom in usuari.items():
            f.write('\t"{0}" : "{1}",\n'.format(user_id, nom.replace('"', '\\"')))
        f.write('}\n')
        f.write('administradors = {\n')
        for user_id in administradors:
            f.write('\t"{0}",\n'.format(user_id))
        f.write('}\n')

def notificar_administradors(missatge):
    for user_id in administradors:
        if user_id in usuari:
            bot.sendMessage(user_id, missatge)

def usuari_desconegut(chat_id, command):
    f = open('/home/pi/Porta/log/ConnexionsNoAutoritzades.log','a')
    id = str('\n' + str(chat_id) + " No Autoritzat <<" + command + ">> " + time.strftime("%H:%M:%S"))
    f.write(id)
    f.close()
    notificar_administradors("Intent no Autoritzat " + str(chat_id) + "\nPer donar-lo d'alta: Nou:" + str(chat_id) + ":Nom usuari")
    return "No Autoritzat"

def llistar_usuaris():
    linies = ["Usuaris:"]
    for user_id, nom in usuari.items():
        rol = " admin" if user_id in administradors else ""
        linies.append(user_id + " - " + nom + rol)
    return "\n".join(linies)

def info_programa(chat_id):
    return "\n".join([
        "Info PortaBombers",
        "Programa: " + os.path.abspath(__file__),
        "Directori: " + os.getcwd(),
        "Config usuaris: " + USERS_CONFIG,
        "Usuari actual: " + str(chat_id),
        "Es admin: " + ("si" if es_admin(chat_id) else "no"),
        "Usuaris carregats: " + str(len(usuari)),
        "Administradors carregats: " + ", ".join(administradors),
    ])

def afegir_usuari(parametres):
    parts = parametres.split(':', 1)
    user_id = parts[0].strip()
    nom = parts[1].strip() if len(parts) > 1 else ""
    if not user_id:
        return "Falta el codi d'usuari"
    if not nom:
        return "Falta el nom de l'usuari. Format: Nou:<codi>:<nom>"
    if user_id in usuari:
        return "Aquest usuari ja existeix: " + user_id
    usuari[user_id] = nom
    guardar_configuracio()
    return "Usuari afegit: " + user_id + " - " + nom

def eliminar_usuari(user_id):
    user_id = user_id.strip()
    if user_id == "3758341":
        return "No es pot eliminar l'administrador principal"
    if user_id not in usuari:
        return "Aquest usuari no existeix: " + user_id
    nom = usuari[user_id]
    del usuari[user_id]
    administradors.discard(user_id)
    guardar_configuracio()
    return "Usuari eliminat: " + user_id + " - " + nom

def assignar_admin(user_id):
    user_id = user_id.strip()
    if user_id not in usuari:
        return "Aquest usuari no existeix: " + user_id
    administradors.add(user_id)
    guardar_configuracio()
    return "Administrador afegit: " + user_id + " - " + usuari[user_id]

def treure_admin(user_id):
    user_id = user_id.strip()
    if user_id == "3758341":
        return "No es pot treure el rol a l'administrador principal"
    if user_id not in administradors:
        return "Aquest usuari no es administrador: " + user_id
    administradors.remove(user_id)
    guardar_configuracio()
    return "Administrador eliminat: " + user_id

def comanda_admin(command, chat_id):
    command = command.strip()
    command_lower = command.lower()
    if command_lower == 'ajuda':
        return ADMIN_HELP
    if command_lower == 'info':
        return info_programa(chat_id)
    if command_lower == 'llista':
        return llistar_usuaris()
    if command_lower.startswith('nou:'):
        return afegir_usuari(command[4:])
    if command_lower.startswith('elimina:'):
        return eliminar_usuari(command[8:])
    if command_lower.startswith('admin:'):
        return assignar_admin(command[6:])
    if command_lower.startswith('noadmin:'):
        return treure_admin(command[8:])
    return None

def on(pin, chat_id):
    if str(chat_id) in usuari:
        nom_usuari = usuari[str(chat_id)]
        f = open('/home/pi/Porta/log/Connexions.log','a')
        GPIO.output(pin,GPIO.HIGH)
        time.sleep(2)
        GPIO.output(pin,GPIO.LOW)
        #Registre accessos
        id = str('\n' + str(chat_id) + ' ' + nom_usuari + " Autoritzat -> " + time.strftime("%H:%M:%S"))
        f.write(id)
        f.close()
        bot.sendMessage(chat_id, "Porta Activada")
        for user in administradors:
            if user in usuari:
                bot.sendMessage(user, "Porta Activada per " + nom_usuari)
        return None
    else:
        f = open('/home/pi/Porta/log/ConnexionsNoAutoritzades.log','a')
        #Registre accessos
        id = str('\n' + str(chat_id) + " No Autoritzat -> " + time.strftime("%H:%M:%S"))
        f.write(id)
        f.close()
        for  user in usuari:
            bot.sendMessage(user, "Intent no Autoritzat "+ str(chat_id))
        return "No Autoritzat"

def off(pin, chat_id, command):
    f = open('/home/pi/Porta/log/ConnexionsNoAutoritzades.log','a')
    GPIO.output(pin,GPIO.LOW)
    if str(chat_id) in usuari:
        #Registre accessos
        id = str('\n' + str(chat_id) + ' ' + usuari[str(chat_id)] + " Cadena incorrecta <<" + command + ">> " + time.strftime("%H:%M:%S"))
        f.write(id)
    else:
        #Registre accessos
        id = str('\n' + str(chat_id) + " Cadena incorrecta <<" + command + ">>" + time.strftime("%H:%M:%S"))
        f.write(id)
    f.close()
    return "Cadena incorrecta"

# to use Raspberry Pi board pin numbers
GPIO.setmode(GPIO.BOARD)
# set up GPIO output channel
GPIO.setup(7, GPIO.OUT)

def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text'].strip()
    if str(chat_id) not in usuari:
        bot.sendMessage(chat_id, usuari_desconegut(chat_id, command))
        return
    resposta_admin = comanda_admin(command, chat_id) if es_admin(chat_id) else None
    if resposta_admin:
        bot.sendMessage(chat_id, resposta_admin)
    elif command.lower() == 'on':
        #Si cadena correcte crido funcio obertura i envio missatge
        resposta = on(7,chat_id)
        if resposta:
            bot.sendMessage(chat_id, resposta)
    else:
        #Si cadena incorrecta crido funcio error i envio missatge
        bot.sendMessage(chat_id, off(7,chat_id, command))

#Activació del bucle d'escolta de missatges de telegram
bot.message_loop(handle)
print("Escoltant")

while 1:
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        f = open('/home/pi/Porta/log/Interrupcions.log','a')
        id = str('\n'+" Programa interrumput per teclat" + time.strftime("%H:%M:%S"))
        f.write(id)
        f.close()
        GPIO.cleanup()
        exit()
    except:
        #Registre error
        f = open('/home/pi/Porta/log/Interrupcions.log','a')
        id = str('\n'+" Programa interrumput per algun error" + time.strftime("%H:%M:%S"))
        f.write(id)
        f.close()
GPIO.cleanup()
