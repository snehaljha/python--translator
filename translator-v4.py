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
		self.tab = []
		self.tfname = None
		self.tfcode = None
		self.addwin = None
		self.dialog = None

		self.menu = Menu(self, bg='lightgrey', fg='black')
		self.langmenu=Menu(self.menu, tearoff=0, bg='lightgrey', fg='black')
		self.langmenu.add_command(label="Add Language", command=self.addlang)
		self.menu.add_cascade(label='Languages', menu=self.langmenu)
		self.config(menu=self.menu)

		self.nb = Notebook(self)
		self.entab = Frame(self.nb)

		translatebutton = Button(self.entab, text='Translate', command=self.translate)
		translatebutton.pack(side=BOTTOM, fill=X)

		self.tf = Text(self.entab, bg='white', fg='black')
		self.tf.pack(side=TOP, fill=BOTH, expand=1)

		self.nb.add(self.entab, text='English')
		self.nb.pack(fill=BOTH, expand=1)
		self.delmenu = Menu(self.menu, tearoff=0, bg='lightgrey', fg='black')
		self.delmenu.add_command(label='Delete Tab', command=self.deltab)
		self.menu.add_cascade(label='Delete', menu=self.delmenu)

		self.delmenu.add_command(label='Delete Language', command=self.dellang)



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
			self.addwin.destroy()
			showinfo("Added", name + " is added successfully")
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
		self.tab.append(ltab)

		


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



	def deltab(self, text=None):
		if text:
			index = self.langtab.index(text)
			tab = self.tab[index]
			self.nb.forget(tab)
			return
		if self.nb.select()!=str(self.entab):
			self.nb.forget(self.nb.select())
		else:
			showerror("Failed", "English tab can't be deleted")


	def dellang(self):
		self.dialog = Toplevel()
		self.dialog.title("Delete Language")
		self.dialog.geometry("150x100")
		button = Button(self.dialog, text='Delete', bg='lightgrey', fg='black', pady=10, font=(20), command=lambda:
			self.removelang(entry))
		entry = Entry(self.dialog, bg='white', fg='black', font=(20))
		label=Label(self.dialog, text='Language Name', bg='lightgrey', fg='black', pady=8, font=(20))
		button.pack(side=BOTTOM, fill=X)
		entry.pack(side=BOTTOM, fill=X)
		label.pack(side=TOP, fill=BOTH, anchor=N)


	def removelang(self, entry):
		text = entry.get()
		if text:
			target=None
			for name in self.langname:
				if text.lower() == name.lower():
					target = name
					break
			if not target:
				showerror("Not Found", "Language not found")
				return
			self.langmenu.delete(target)
			self.deltab(target)
			self.dialog.destroy()
			showinfo('Deleted', target + " deleted successfully")
		else:
			showerror('Blank', 'You had not entered anything')


win = translator()
win.mainloop()