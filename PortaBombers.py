#coder :- Oriol Riu

import sys
import time
import telepot
import RPi.GPIO as GPIO
import time
from config.users import usuari, TOKEN

#Usuaris

# capto el token de la linea de comandos

bot = telepot.Bot(TOKEN) #activo l'escolta del bot

# Configuracio per utilitzar Raspberry Pi board pin numbers
GPIO.setmode(GPIO.BOARD)
# Activo GPIO output channel
GPIO.setup(7, GPIO.OUT)

def on(pin, chat_id):
    if str(chat_id) in usuari:
        f = open('/home/pi/Porta/log/Connexions.log','a')
        GPIO.output(pin,GPIO.HIGH)
        time.sleep(2)
        GPIO.output(pin,GPIO.LOW)
        #Registre accessos
        id = str('\n' + str(chat_id) + ' ' + usuari[str(chat_id)] + " Autoritzat -> " + time.strftime("%H:%M:%S"))
        f.write(id)
        f.close()
        for  user in usuari:
            bot.sendMessage(user, "Porta Activada per "+usuari[str(chat_id)])
        return "Autoritzat"
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
    if usuari[str(chat_id)]:
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
    command = msg['text']
    if command == 'on' or command =='On':
        #Si cadena correcte crido funcio obertura i envio missatge
        bot.sendMessage(chat_id, on(7,chat_id))
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
