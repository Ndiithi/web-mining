'''
Created on Feb 19, 2018

@author: duncan
'''


from Tkinter import *
from tkFileDialog   import askopenfilename
from tkMessageBox import *


def NewFile():
    print "New File!"
def OpenFile():
    name = askopenfilename()
    print name
def About():
    print "This is a simple example of a menu"
    
root = Tk()
root.title('G-mailer')
root.minsize(500,500)
root.geometry("800x600")


menu = Menu(root)
root.config(menu=menu)

filemenu = Menu(menu)
menu.add_cascade(label="Bot", menu=filemenu)
filemenu.add_command(label="Add recipients")
filemenu.add_command(label="Add accounts")
filemenu.add_command(label="Set mail message")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)

settings_menu = Menu(menu)
menu.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Error mail")
settings_menu.add_command(label="Account Threshold")

reports_menu = Menu(menu)
menu.add_cascade(label="Reports", menu=reports_menu)
reports_menu.add_command(label="Campaign Status")
reports_menu.add_command(label="Error Reports")
reports_menu.add_command(label="Pending Reports")


def answer():
    showerror("Answer", "Sorry, no answer available")

def callback():
    if askyesno('Verify', 'Really quit?'):
        showwarning('Yes', 'Not yet implemented')
    else:
        showinfo('No', 'Quit has been cancelled')

Button(text='Quit', command=callback).grid(row=0)
Button(text='Answer', command=answer).grid(row=0,column=1)

mainloop()
