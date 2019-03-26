#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import tkinter as tk
from tkinter import messagebox
import pickle


class LoginFrame(tk.Frame):#genere une frame pour le login screen
    def __init__(self, master):
        super().__init__(master)
        self.login_statut = False


        self.label_username = tk.Label(self, text="Username")
        self.label_servername = tk.Label(self, text="Server name")
        self.label_port = tk.Label(self, text="Port")


        self.entry_username = tk.Entry(self)
        self.entry_servername = tk.Entry(self)
        self.entry_port = tk.Entry(self)

        self.label_username.grid(row=0)
        self.label_servername.grid(row=1)
        self.label_port.grid(row=2)
        
        self.entry_username.grid(row=0, column=1)
        self.entry_servername.grid(row=1, column=1)
        self.entry_port.grid(row=2, column=1)

        self.logbtn = tk.Button(self, text="Login", command=self._login_btn_clicked)
        self.logbtn.grid(columnspan=2)

        self.pack()


    def get_statut(self):
    	return self.login_statut

    def get_username(self):
    	return self.entry_username.get()
    def get_servername(self):
    	return self.entry_servername.get()
    def get_port(self):
    	return self.entry_port.get()


    def _login_btn_clicked(self):
        # print("Clicked")
        username = self.entry_username.get()
        servername = self.entry_servername.get()
        port = self.entry_port.get()
        # print(username, servername)

        if username == "john" and servername == "servername":
            tk.messagebox.showinfo("Login info", "Welcome John")
        else:
            tk.messagebox.showerror("Login error", "Incorrect username")

def usr_login():
    pass    

class GUI:
    """docstring for GUI"""
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Chat client")
        self.window.geometry("400x600")
        #login step
        loginframe = LoginFrame(self.window)
        while(loginframe.get_statut() != "ok"):
        	loginframe.login_statut = input("put")
        
        #print("out")
        self.username = loginframe.get_username()
        self.servername = loginframe.get_servername()
        self.port = loginframe.get_port()

        loginframe.destroy()
        print("port:",self.username)
        print("servername:",self.servername)
        print("port:",self.port)
        self.window.mainloop()


class Application:
	def __init(self):
		_gui = GUI()
		

if __name__ == '__main__':
    Application = GUI()
