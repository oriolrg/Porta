#!/bin/bash
# Instalació Porta
# crontab exec a l'arrancar @reboot python3 /XXX/XX/Porta/OberturaPorta.py

cp users\ copy.py config/users.py
mkdir log
#instalar python3
sudo apt install python3
#Instalar telepot python 3
sudo pip3 install telepot
