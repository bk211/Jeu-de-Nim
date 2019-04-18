from tkinter import *
import tkinter.messagebox as tm


class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)

        self.label_username = Label(self, text="Username")
        self.label_servername = Label(self, text="Server name")
        self.label_port = Label(self, text="Port")


        self.entry_username = Entry(self)
        self.entry_servername = Entry(self)
        self.entry_port = Entry(self)

        self.label_username.grid(row=0, sticky=E)
        self.label_servername.grid(row=1, sticky=E)
        self.label_port.grid(row=2, sticky=E)

        self.entry_username.grid(row=0, column=1)
        self.entry_servername.grid(row=1, column=1)
        self.entry_port.grid(row=2, column=1)

        self.logbtn = Button(self, text="Login", command=self._login_btn_clicked)
        self.logbtn.grid(columnspan=2)

        self.pack()

    def _login_btn_clicked(self):
        # print("Clicked")
        username = self.entry_username.get()
        servername = self.entry_servername.get()
        port = self.entry_port.get()
        # print(username, servername)

        if username == "john" and servername == "servername":
            tm.showinfo("Login info", "Welcome John")
        else:
            tm.showerror("Login error", "Incorrect username")


root = Tk()
lf = LoginFrame(root)
root.mainloop()
