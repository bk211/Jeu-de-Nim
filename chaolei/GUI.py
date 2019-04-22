#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import tkinter as tk
import os
from tkinter import messagebox
import pickle
from client_alone import Client
import time
import threading
from multiprocessing import Queue

##genere une frame uniquement dédié pour le login screen
class LoginFrame(tk.Frame):
    ##Le constructeur
    def __init__(self, master):
        super().__init__(master)
        self.login_statut = False
        self.username = ""
        self.servername = ""
        self.port = ""

        self.label_username = tk.Label(self, text="Username")
        self.label_servername = tk.Label(self, text="Server name")
        self.label_port = tk.Label(self, text="Port")


        self.entry_username = tk.Entry(self, state='disabled')
        self.entry_servername = tk.Entry(self)
        self.entry_port = tk.Entry(self)

        self.label_username.grid(row=0)
        self.label_servername.grid(row=1)
        self.label_port.grid(row=2)

        self.entry_username.grid(row=0, column=1)
        self.entry_servername.grid(row=1, column=1)
        self.entry_port.grid(row=2, column=1)

        self.logbtn = tk.Button(self, text="Connect", command=self.connect)
        self.logbtn.grid(columnspan=2)

        self.pack()

    ## renvoie la statut qui indique si on est loggé ou non
    def get_statut(self):
    	return self.login_statut
    ## renvoie username
    def get_username(self):
    	return self.username
    ## renvoie le nom de server
    def get_servername(self):
    	return self.servername
    ## renvoie le port
    def get_port(self):
    	return self.port


    ## Function pour se connecté, il est bind à au boutton connecte
    def connect(self):
        self.servername = self.entry_servername.get()
        self.port = self.entry_port.get()

        if user_login(self.servername, self.port):# si login reussi
            messagebox.showinfo("Connect attempt", "Succeded to connect,merci d'entrer votre pseudo")
            self.entry_username.config(state='normal')#ouverture de la saisit du pseudo
            self.entry_servername.config(state= 'disabled')#caché
            self.entry_port.config(state= 'disabled')#caché
            self.logbtn.config(command = self.log_in, text="log-in")
        else:
            messagebox.showinfo("Connect attempt", "Failed to connect")
    def log_in(self):
        ## fonction pour envoyer son pseudo
        global my_client
        self.username = self.entry_username.get()
        my_client.send_client_name(self.username)
        time.sleep(0.1)
        if my_client.get_name_statut():
            messagebox.showinfo("Log-in attempt", "Succeded to log-in")
            self.login_statut = True
            self.pack_forget()#reussite, les champs de login sont effacé
        else:
            messagebox.showinfo("Log-in attempt", "Failed to log-in, please re-try with another name")

## fonction qui essait de se connecter
def user_login(servername, port):
    try:
        global my_client
        my_client = Client(servername, int(port), True)
    except:
        return False
    if my_client.get_connect_statut():
        return True
    return False

class GUI:
    """class GUI"""
    def __init__(self):

        self.window = tk.Tk()
        self.window.title("Chat client")
        self.window.geometry("800x600")
        ##login step
        self.loginframe = LoginFrame(self.window)

        ##frame qui contiendra les messages
        self.messages_frame = tk.Frame(self.window)
        ## variable user pour recuperer la saisit utilisateur
        self.user_msg = tk.StringVar()
        ## listbox pour afficher les messages passé
        self.messages_listbox = tk.Listbox(self.window,height=15, width = 50 ,bg="white")
        self.messages_listbox.pack(fill = tk.X)
        self.messages_listbox.pack()
        self.messages_frame.pack()
        ## champs d'entrée utilisateur
        self.entry_field = tk.Entry(self.window, textvariable=self.user_msg)
        self.entry_field.pack()
        ## boutton qui permet envoie des données
        self.bottom_button = tk.Button(self.window, text="Send message", command=self.send_message)
        self.bottom_button.pack()
        ## boutton qui permet de lancer le jeu
        self.start_game_button = tk.Button(self.window, text="Start Game", command=self.start_game)
        self.start_game_button.pack()
        self.bottom_button.pack()

        ## label qui contiendra le pseudo
        self.label_username_text = tk.StringVar()
        self.label_username_text.set("Username: ")
        self.label_username = tk.Label(self.window, textvariable = self.label_username_text)
        self.label_username.pack()

        ## label qui contiendra le portefeuille du joueur
        self.label_wallet_text = tk.StringVar()
        self.label_wallet_text.set("Bank :")
        self.label_wallet = tk.Label(self.window, textvariable = self.label_wallet_text)
        self.label_wallet.pack()

        ## label qui contiendra les cartes du joueur
        self.label_cards_text = tk.StringVar()
        self.label_cards_text.set("Cards :")
        self.label_cards =tk.Label(self.window, textvariable=self.label_cards_text)
        self.label_cards.pack()

        ## le request actuelle demandé par le serveur
        self.current_request = "None"

        self.allow_treating = False
        ## lance le thread de traitement
        self.start_treat()
        self.window.mainloop()

    def start_game(self):
        ##fonction qui tente de lancer le jeu en envoyant le signal STR
        try:
            my_client.send_msg("STR")
        except:
            return

    def send_message(self):
        ## envoie le message saisit par utilisateur
        raw =self.entry_field.get()
        data = "MSG {} {}".format(self.loginframe.get_username(),raw)
        try:
            my_client.send_msg(data)
            self.entry_field.delete(0,"end")#envoie reussit, le champs est réinitialiser
        except:
            return

    def reply_to_req(self):
        ## Réponds à une requete du serveur
        raw =self.entry_field.get()
        data = "{} {}".format(self.current_request,raw)
        my_client.send_msg(data)
        self.reset_bottom_button()
        #réponse effectué, on redonne le droit d'envoyer des messages


    def start_treat(self):
        ## lance le thread de traitement
        self.allow_treating = True
        thread_treat = threading.Thread(target =self.treating)
        thread_treat.start()

    def reset_bottom_button(self):
        ## réinitialise boutton principal et efface le champs de saisit utilisateur
        self.entry_field.delete(0,"end")
        self.bottom_button.config(state='normal', text= "send message",command = self.send_message)

    def push_to_mbox(self, content):
        ## Envoie le contenue passé en paramètre au champs des messages
        self.messages_listbox.insert(tk.END, content)

    def set_req(self, req):
        ## modifie le binding du boutton principal afin d'effectuer une réponse
        # à une requetes
        self.current_request = req
        self.bottom_button.config(text=self.current_request,command = self.reply_to_req)

    def treating(self):
        while self.allow_treating:
            # si on est loggué
            if self.loginframe.get_statut():
                global my_client
                data = my_client.get_event()
#                print("from GUI::",data)
#debugg line
# similairement, c'est quasiment la même compréhension de liste que chez le client
# on n'affiche plus au terminal mais plutot au champs dédié du GUI
                if data[0] == "LFT":
                    self.push_to_mbox("Player {} has left".format(data[1]))
                elif data[0] == "WHO":
                    self.label_username_text.set("Username :"+self.loginframe.get_username())
                elif data[0] == "MSG":
                    self.push_to_mbox("{} : {}".format(data[1], " ".join(data[2:])))
                elif data[0] == "BYE":
                    self.push_to_mbox("{} : {}".format("SYS","Deconnection avec le serveur"))
                elif data[0] == "ERR":
                    self.push_to_mbox(">>Erreur recu : {} ".format(data[1:]))

                elif data[0] == "ANN":
                    if data[1] == "PUT":
                        self.push_to_mbox(">>Le joueur {} a mise {} ".format(data[2],data[3]))
                    if data[1] == "PLY":
                        self.push_to_mbox(">>Le joueur {} a joué {} ".format(data[2],data[3]))
                    if data[1] == "WIN":
                        self.push_to_mbox(">>Le joueur {} a gagné {} ".format(data[2],data[3]))
                    if data[1] == "LOS":
                        self.push_to_mbox(">>Le joueur {} a perdu {} ".format(data[2],data[3]))
                    if data[1] == "VIC":
                        self.push_to_mbox(">>Le joueur {} remporte la victoire ".format(data[2]))

                elif data[0] == "ARV":
                    self.push_to_mbox(">>New player has joined {}".format(data[1]))

                elif data[0] == "GET":
                    self.push_to_mbox(">>Distribution de cartes en cours")
                    self.label_cards_text.set("Cards : {}".format(data[1:]))

                elif data[0] == "REQ":
                    if data[1] == "PUT":
                        self.push_to_mbox("{} : {}".format("Croupier","Entrez votre mise, vous disposez de {} jetons".format(data[2])))
                        self.label_wallet_text.set("Bank : {}".format(data[2]))
                        self.set_req("PUT")
                    if data[1] == "PLY":
                        self.push_to_mbox("{} : {}".format("Croupier","Merci de jouer une carte"))
                        self.set_req("PLY")

                else:
                    print(">>none of switch meet, here is the raw data : "," ".join(data))

my_client = None

if __name__ == '__main__':
    Application = GUI()
