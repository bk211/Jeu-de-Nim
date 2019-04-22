#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import tkinter as tk
from tkinter import messagebox
import pickle
from client_alone import Client
import time
import threading
from multiprocessing import Queue

class LoginFrame(tk.Frame):#genere une frame pour le login screen
    def __init__(self, master):
        super().__init__(master)
        self.login_statut = False
        self.username = ""
        self.servername = ""
        self.port = ""

        #print("reached")
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


    def get_statut(self):
    	return self.login_statut
    def get_username(self):
    	return self.username
    def get_servername(self):
    	return self.servername
    def get_port(self):
    	return self.port


    def connect(self):
        # print("Clicked")
        self.servername = self.entry_servername.get()
        self.port = self.entry_port.get()
        #self.login_statut = True
        if user_login(self.servername, self.port):
            messagebox.showinfo("Connect attempt", "Succeded to connect,merci d'entrer votre pseudo")
            self.entry_username.config(state='normal')
            self.entry_servername.config(state= 'disabled')
            self.entry_port.config(state= 'disabled')
            self.logbtn.config(command = self.log_in)
        else:
            messagebox.showinfo("Connect attempt", "Failed to connect")
    def log_in(self):
        global my_client
        self.username = self.entry_username.get()
        my_client.send_client_name(self.username)
        time.sleep(1)
        if my_client.get_name_statut():
            messagebox.showinfo("Log-in attempt", "Succeded to log-in")
            self.pack_forget()
            Global Events_queue
            Events_queue.put("LOG")
        else:
            messagebox.showinfo("Log-in attempt", "Failed to log-in, please re-try with another name")


def user_login(servername, port):
    try:
        global my_client
        my_client = Client(servername, int(port))
    except:
        return False
    print(my_client.get_connect_statut())
    if my_client.get_connect_statut():
        return True
    return False

class GUI:
    """docstring for GUI"""
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Chat client")
        self.window.geometry("800x600")
        #login step
        loginframe = LoginFrame(self.window)
        self.start_treat
        self.window.mainloop()

    def start_treat(self):
        thread_treat = threading.Thread(target =self.treating)
        thread_treat.start()

    def treating(self):
        while True:
            Global Events_queue
            data = Events_queue.get()
            if data == "LOG":
                print("LOG DONE , creating game screen")


my_client = None
Events_queue = Queue()

if __name__ == '__main__':
    Application = GUI()
