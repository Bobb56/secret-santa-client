"""
Ceci est le client pour participer au SecretSanta ENS Rennes info. Il est distribué sans license.
"""
import time
import os
import socket
import sys

try:
    from rsa import *
except:
    print("Le client secret santa a besoin du module python rsa pour fonctionner.")
    print("> Vous pouvez essayer la commande `pip install rsa`. Normalement sur Windows, ça fonctionne.")
    print("\n> Si la commande ne fonctionne pas, essayez d'installer le paquet `python3-rsa` avec votre gestionnaire de paquets habituel")
    print("\n> Enfin, si ça ne fonctionne toujours pas, créez un environnement virtuel et installez rsa dedans :")
    print(" > Commencez par taper la commande `python3 -m venv myenv`")
    print(" > Puis tapez la commande `source myenv/bin/activate` afin de rentrer dans l'environnement virtuel")
    print(" > Lancez la commande `pip install rsa`")
    print(" > Vous pouvez relancer le client secret santa !")
    print(" > Une fois terminé, tapez la commande `deactivate` pour sortir de l'environnement virtuel")
    print(" > A chaque fois que vous voudrez exécuter le client, il faudra au préalable se mettre dans l'environnement virtuel")
    sys.exit()

HOST = '2a02:8424:8781:7901:ce43:8e88:c2db:5d82'  # ou l'adresse IP de mon serveur
PORT = 12345

save_file = "CONSERVER CE FICHIER"

def make_bin(hexstring):
    intlist = [int(hexstring[i:i+2], 16) for i in range(0, len(hexstring), 2)]
    return bytes(intlist)




def slow_print(*args, end = "\n", sep = " "):
    string = sep.join(args) + end
    for c in string:
        print(c, end = '')
        time.sleep(0.02)
        sys.stdout.flush()


def slow_input(prompt = ''):
    for c in prompt:
        print(c, end = '')
        time.sleep(0.02)
        sys.stdout.flush()
    
    try:
        ans = input()
    except (KeyboardInterrupt, EOFError):
        sys.exit()
    
    return ans


def pause():
    try:
        input()
    except KeyboardInterrupt:
        sys.exit()



def request(function, args):
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(bytes(function + '\0' + args, "utf-8"))
            data = s.recv(1024)

        return data.decode()
    except :
        slow_print("Erreur lors de la connexion au serveur.")
        sys.exit()


def secretsantaserver_getPhase():
    return request("getPhase", "")

def secretsantaserver_getAllNames():
    return eval(request("getAllNames", ""))

def secretsantaserver_addName(name):
    (pubkey, privkey) = newkeys(768)
    request("addName", name + '\0' + str(pubkey))
    return str(privkey)

def secretsantaserver_decode(name, privkey):
    crypto = make_bin(request("decode", name))
    return decrypt(crypto, privkey).decode()




def print_names(names):
    for name in names:
        slow_print(' >', name)



def subscribe():
    if os.path.isfile(save_file):
        slow_print("Vous êtes déjà inscrit, veuillez relancer le programme plus tard pour savoir à qui vous allez offrir un cadeau")
        return

    slow_print("Vous êtes sur le point de vous inscrire au Secret Santa.\nIl est important de noter que vous ne pouvez vous inscrire qu'une seule fois, et uniquement avec votre vrai nom.")
    slow_print("Appuyez sur [ENTREE] quand vous êtes prêt.e.")
    pause()

    names = secretsantaserver_getAllNames()

    if len(names) > 0:
        slow_print("Voici la liste des gens déjà inscrits :")
        print_names(names)

        ans = slow_input("Votre nom apparaît-il déjà dans la liste ? (o/n) : ")

        if ans == 'o':
            slow_print("Veuillez contacter raphael.le-puillandre@ens-rennes.fr")
            sys.exit()
    
    
    name = slow_input("Votre nom ? ")
    while name in names:
        slow_print("Vous ne pouvez pas vous inscrire avec le nom de quelqu'un d'autre.")
        name = slow_input("Votre nom ? ")

    key = secretsantaserver_addName(name)

    f = open(save_file, "w+")
    f.write(str((key, name)))
    f.close()

    slow_print("Et voilà, vous êtes inscrit.e. Quand tout le monde se sera inscrit, réexécutez ce programme pour apprendre à qui vous devrez offrir un cadeau.")
    


def decode():
    slow_print("Bienvenue dans la seconde phase. Vous êtes sur le point de savoir à qui vous allez offir un cadeau.")
    names = secretsantaserver_getAllNames()    

    try:
        f = open(save_file, "r")
        (privkey, name) = eval(f.read())
        f.close()
        
        privkey = eval(privkey)
        message = secretsantaserver_decode(name, privkey)
    except:
        slow_print("Une erreur a eu lieu. Votre inscription est invalide.")
        return

    if message == "ERROR":
        slow_print("Une erreur a eu lieu. Votre inscription est invalide.")
    else:
        slow_input("Appuyez sur [ENTREE] vous prêt.e")
        slow_print("Vous allez offrir un cadeau à...")
        time.sleep(1)
        slow_print("Roulements de tambour...")
        time.sleep(2)
        slow_print(message, '!')






def main():
    phase = secretsantaserver_getPhase()

    if phase == "subscribe":
        subscribe()
    elif phase == 'decode':
        decode()
    else:
        slow_print("Veuillez patienter, la phase d'inscriptions n'a pas encore commencé.")


main()
