#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import tkinter as tk
from tkinter import messagebox
import pickle

def usr_login():
    pass    

def on_hit():
    tk.messagebox.showinfo(title= "Name requiered",message="Please enter your name")

class GUI(object):
    """docstring for GUI"""
    def __init__(self, arg):
        super(GUI, self).__init__()
        self.arg = arg
        self.window = tk.Tk()
        self.window.title("Chat client")
        self.window.geometry("400x600")

        self.pseudo = tk.StringVar()
        self.pseudo.set('hhhhhh')

        pseudoInput = tk.Label(self.window,
            textvariable = self.pseudo,
            bg = 'grey', width = 15, height = 2)

        pseudoInput.pack()


        tk.Label(self.window, text='User name: ').place(x=50, y= 150)
        tk.Label(self.window, text='Server name: ').place(x=50, y= 170)
        tk.Label(self.window, text='Port: ').place(x=50, y= 190)
        
        var_usr_userName = tk.StringVar()
        var_usr_userName.set('bk211')
        entry_usr_userName = tk.Entry(self.window, textvariable=var_usr_userName)
        entry_usr_userName.place(x=160, y=150)
    
        var_usr_serverName = tk.StringVar()
        var_usr_serverName.set('Pablo.Rauzy.com')
        entry_usr_serverName = tk.Entry(self.window, textvariable=var_usr_serverName)
        entry_usr_serverName.place(x=160, y=170)

        var_usr_port = tk.StringVar()
        var_usr_port.set('4567')
        entry_usr_port = tk.Entry(self.window, textvariable=var_usr_port)
        entry_usr_port.place(x=160, y=190)
        confirmButton=tk.Button(self.window, text='hit me', command=on_hit)
        confirmButton.place(x = 150, y = 220)

        self.window.mainloop()

if __name__ == '__main__':
    gui = GUI(123)
