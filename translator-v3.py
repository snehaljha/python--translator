from tkinter import *
from tkinter.ttk import Notebook
from tkinter.messagebox import *
import requests


class translator(Tk):
	def __init__(self):
		super().__init__()
		self.title("Translator")
		self.geometry("500x300")

		self.langname = []
		self.langcode = []
		self.langans = []
		self.langtab= []
		self.langlabel = []
		self.tfname = None
		self.tfcode = None
		self.addwin = None

		self.menu = Menu(self, bg='lightgrey', fg='black')
		self.langmenu=Menu(self.menu, tearoff=0, bg='lightgrey', fg='black')
		self.langmenu.add_command(label="Add Language", command=self.addlang)
		self.menu.add_cascade(label='Languages', menu=self.langmenu)
		self.config(menu=self.menu)

		self.nb = Notebook(self)
		entab = Frame(self.nb)

		translatebutton = Button(entab, text='Translate', command=self.translate)
		translatebutton.pack(side=BOTTOM, fill=X)

		self.tf = Text(entab, bg='white', fg='black')
		self.tf.pack(side=TOP, fill=BOTH, expand=1)

		self.nb.add(entab, text='English')
		self.nb.pack(fill=BOTH, expand=1)



	def addlang(self):
		self.addwin = Toplevel()
		self.addwin.title("Add Language")
		self.addwin.geometry("300x150")

		topframe = Frame(self.addwin, pady=10, height=70)
		midframe = Frame(self.addwin, pady=10, height=70)
		bottomframe = Frame(self.addwin)


		name = Label(topframe, text='Language Name', bg='lightgrey', fg='black', font = (20))
		name.pack(side=LEFT, fill=BOTH, expand=1)

		self.tfname = Text(topframe, height=1, bg='white', fg='black', font=(20))
		self.tfname.pack(side=RIGHT, fill=BOTH, expand=1)

		code = Label(midframe, text='Language Code', bg='lightgrey', fg='black', font=(20))
		code.pack(side=LEFT, fill=BOTH, expand=1)

		self.tfcode = Text(midframe, height=1, bg='white', fg='black', font=(20))
		self.tfcode.pack(side=RIGHT, fill=BOTH, expand=1)

		submit = Button(bottomframe, text='Add', bg='lightgrey', fg='black', pady=10, command=self.submitentry, font=(20))
		submit.pack(fill=X)

		bottomframe.pack(side=BOTTOM, fill=X)
		midframe.pack(side=BOTTOM, fill=BOTH, expand=1)
		topframe.pack(side=TOP, fill=BOTH, expand=1, anchor=N)



	def submitentry(self):
		name = self.tfname.get(1.0, END).strip()
		code = self.tfcode.get(1.0, END).strip()
		if name and code:
			self.langmenu.add_command(label=name, command=lambda:
				self.addtab(name))
			self.langname.append(name)
			self.langcode.append(code)
			showinfo("Added", name + " is added successfully")
			self.addwin.destroy()
		else:
			showerror("Missing Info", "Please add both language name and code")



	def addtab(self, txt):
		ltab = Frame(self.nb)

		ans = StringVar(ltab)
		ans.set(txt + "translation")
		self.langlabel.append(ans)

		self.langtab.append(txt)
		self.langans.append(str(txt + "translation"))
		index = self.langtab.index(txt)

		button = Button(ltab, text='Copy to Clipboard', bg='lightgrey', fg='black', pady=10, command=lambda:
			self.copytoclip(self.langans[index]))
		button.pack(side=BOTTOM, fill=X)

		label = Label(ltab, textvar=ans, bg='lightgrey', fg='black')
		label.pack(side=TOP, fill=BOTH, expand=1)
		self.nb.add(ltab, text=txt)



	def copytoclip(self, text):
		self.clipboard_clear()
		self.clipboard_append(text)
		showinfo('Copied', 'Message copied Successfully')



	def translate(self):
		que = self.tf.get(1.0, END).strip()

		self.langans = []
		err=0


		for i in self.langtab:
			index = self.langname.index(i)
			code = self.langcode[index]
			url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={}&dt=t&q={}".format(code, que)
			try:
				r=requests.get(url)
				r.raise_for_status()
				self.langans.append(r.json()[0][0][0])
			except Exception as e:
				showerror("Failed", "Failed for " + i + " error: " + str(e))
				err=1
		if err==0:
			showinfo("Successful", "Translation Successful")


		for i in range(0, len(self.langans)):
			self.langlabel[i].set(self.langans[i])


win = translator()
win.mainloop()