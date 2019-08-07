from tkinter import *
from tkinter.ttk import Notebook
from tkinter.messagebox import *
import requests
import sqlite3
import os


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
		self.proxy = None
		self.proxyentry = None
		self.proxystate = 0
		self.pwin = None

		self.menu = Menu(self, bg='lightgrey', fg='black')
		self.langmenu=Menu(self.menu, tearoff=0, bg='lightgrey', fg='black')
		self.langmenu.add_command(label="Add Language", command=self.addlang)
		self.proxymenu=Menu(self.menu, tearoff=0, bg='lightgrey', fg='black')
		self.proxymenu.add_command(label="Set Proxy", command=self.setproxy)
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

		self.menu.add_cascade(label='Proxy', menu=self.proxymenu)


		if not os.path.isfile("lcodes.db"):
			self.conn = sqlite3.connect("lcodes.db")
			self.cur = self.conn.cursor()
			self.cur.execute('CREATE TABLE languages (name TEXT, code TEXT)')
		else:
			self.conn = sqlite3.connect("lcodes.db")
			self.cur = self.conn.cursor()
			self.cur.execute('SELECT * FROM languages ORDER BY name')
			self.fromdb()


		if os.path.isfile('proxy.txt'):
			f = open("proxy.txt", "rt")
			pr = f.readline()
			if len(pr)>0:
				self.proxystate=1
				self.proxy = {"https":"https://"+pr}
			f.close()



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
			if (code in self.langcode) or (name in self.langname):
				showerror('Exists', 'Language alredy added')
				return
			self.langmenu.add_command(label=name, command=lambda:
				self.addtab(name))
			self.langname.append(name)
			self.langcode.append(code)
			st = "INSERT INTO languages\nVALUES ('" + name + "', '" + code + "');"
			self.cur.execute(st)
			self.conn.commit()
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
		que = self.tf.get(1.0, END)

		self.langans = []
		err=0

		for i in self.langtab:
			index = self.langname.index(i)
			code = self.langcode[index]
			url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl={}&dt=t&q={}".format(code, que)
			try:
				if self.proxystate==1:
					r=requests.get(url, proxies=self.proxy)
				else:
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
			if not text in self.langtab:
				return
			index = self.langtab.index(text)
			tab = self.tab[index]
			self.nb.forget(tab)
			return
		if self.nb.select()!=str(self.entab):
			target = None
			for i in self.tab:
				if self.nb.select()==str(i):
					target = i
					break
			index = self.tab.index(target)
			self.tab.remove(target)
			self.langlabel.pop(index)
			self.langtab.pop(index)
			self.langans.pop(index)
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
			self.dialog.destroy()
			index = self.langname.index(target)
			code = self.langcode[index]
			self.langname.remove(target)
			self.langcode.remove(code)
			'''index=self.langtab.index(target)
			self.langtab.remove(target)
			self.tab.pop(index)
			self.langans.pop(index)
			self.langlabel.pop(index)'''
			st = 'DELETE FROM languages WHERE code = "' + code + '";'
			self.cur.execute(st)
			self.conn.commit()
			showinfo('Deleted', target + " deleted successfully")
		else:
			showerror('Blank', 'You had not entered anything')



	def fromdb(self):
		self.cur.execute('SELECT * FROM languages')
		data = self.cur.fetchall()
		for row in data:
			self.langname.append(row[0])
			self.langcode.append(row[1])
			self.langmenu.add_command(label=row[0], command=lambda:
				self.addtab(row[0]))


	def setproxy(self):
		self.pwin = Toplevel()
		self.pwin.title("Proxy")
		label = Label(self.pwin, text='proxy(hostname:port)', fg='black', bg='lightgrey')
		self.proxyentry = Entry(self.pwin, fg='black', bg='white')
		subbutton = Button(self.pwin, text='submit', fg='black', bg='lightgrey', command=lambda:
			self.applyproxy(1))
		dupbutton = Button(self.pwin, text="Don't use proxy", fg='black', bg='lightgrey', command=lambda:
			self.applyproxy(0))
		label.grid(row=0, column=0)
		self.proxyentry.grid(row=0, column=1)
		subbutton.grid(row=1, columnspan=2)
		dupbutton.grid(row=2, columnspan=2)


	def applyproxy(self, n):
		if n==0:
			self.proxystate = 0
			f = open("proxy.txt", "wt")
			f.write("")
			f.close()
			self.pwin.destroy()
			return
		proxy=self.proxyentry.get(1.0,END).strip()
		self.proxystate=1
		self.proxy={"https":"https://"+proxy}
		f = open("proxy.txt", "wt")
		f.write(proxy)
		f.close()
		self.pwin.destroy()



win = translator()
win.mainloop()