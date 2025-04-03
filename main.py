import tkinter.messagebox
from tkinter import *

win = Tk()
win.title('University Student Registration System')
win.geometry('500x200')


def submit_info():
    tkinter.messagebox.showinfo("Success","Information Saved Successfully")


btn = Button(win, text="Submit", width=len("submit")+1, height=2, command=submit_info)
btn.place(x=200, y=30)
win.mainloop()
