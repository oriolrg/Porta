import sys
import time
import telepot

#Script per obtenir Id dels telefons afegir token a l'executar
TOKEN = sys.argv[1]
bot = telepot.Bot(TOKEN)
def handle(msg):
    chat_id = msg['chat']['id']
    print(str(chat_id))
bot.message_loop(handle)
print("Escoltant")

while 1:
        try:
                time.sleep(10)
        except KeyboardInterrupt:
                exit()