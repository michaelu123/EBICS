from tkinter import *
from tkinter.filedialog import askopenfilenames, askopenfilename
from tkinter.messagebox import *

import os
import locale
from ebics import Ebics


class ButtonEntry(Frame):
    def __init__(self, master, buttontext, stringtext, w, cmd):
        super().__init__(master)
        self.btn = Button(self, text=buttontext, bg="red", bd=4, width=15, height=0, relief=RAISED, command=cmd)
        self.svar = StringVar()
        self.svar.set(stringtext)
        self.entry = Entry(self, textvariable=self.svar, bd=4,
                           width=w, borderwidth=2)
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.btn.grid(row=0, column=0, sticky="w")
        self.entry.grid(row=0, column=1, sticky="we")

    def get(self):
        return self.svar.get()

    def set(self, s):
        return self.svar.set(s)

class LabelEntry(Frame):
    def __init__(self, master, labeltext, stringtext, w):
        super().__init__(master)
        self.label = Label(self, text=labeltext, bd=4, width=15, height=0, relief=RIDGE)
        self.svar = StringVar()
        self.svar.set(stringtext)
        self.entry = Entry(self, textvariable=self.svar, bd=4,
                           width=w, borderwidth=2)
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.label.grid(row=0, column=0, sticky="w")
        self.entry.grid(row=0, column=1, sticky="we")

    def get(self):
        return self.svar.get()

    def set(self, s):
        return self.svar.set(s)

class LabelOM(Frame):
    def __init__(self, master, labeltext, options, initVal, **kwargs):
        super().__init__(master)
        self.options = options
        self.label = Label(self, text=labeltext, bd=4, width=15, relief=RIDGE)
        self.svar = StringVar()
        self.svar.set(initVal)
        self.optionMenu = OptionMenu(self, self.svar, *options, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.label.grid(row=0, column=0, sticky="w")
        self.optionMenu.grid(row=0, column=1, sticky="w")

    def get(self):
        return self.svar.get()

    def set(self, s):
        self.svar.set(s)


class MyApp(Frame):
    def __init__(self, master):
        super().__init__(master)
        w = 50
        self.inputFilesBE = ButtonEntry(master, "Eingabedateien", "", w, self.inpFilesSetter)
        self.templateBE = ButtonEntry(master, "Template-Datei", "", w, self.templFileSetter)
        self.outputLE = LabelEntry(master, "Ausgabedatei", "ebics.xml", w)
        self.betragLE = LabelEntry(master, "Betrag", "100,00", w)
        self.zweckLE = LabelEntry(master, "Zweck", "ADFC Fahrradkurs", w)
        self.mandatLE = LabelEntry(master, "Mandat", "ADFC-M-RFS-2018", w)
        self.sepOM = LabelOM(master, "CSV Separator", ["Komma", "Semikolon"], "Komma")
        self.startBtn = Button(master, text="Start", bd=4, bg="red", width=15, command = self.starten)
        for x in range(1):
            Grid.columnconfigure(master, x, weight=1)
        for y in range(8):
            Grid.rowconfigure(master, y, weight=1)

        self.inputFilesBE.grid(row=0, column=0, sticky="we")
        self.templateBE.grid(row=1, column=0, sticky="we")
        self.outputLE.grid(row=2, column=0, sticky="we")
        self.betragLE.grid(row=3, column=0, sticky="we")
        self.zweckLE.grid(row=4, column=0, sticky="we")
        self.mandatLE.grid(row=5, column=0, sticky="we")
        self.sepOM.grid(row=6, column=0, sticky="w")
        self.startBtn.grid(row=7, column=0, sticky="w")

    def inpFilesSetter(self):
        x = askopenfilenames(title = "CSV Dateien auswählen", defaultextension = ".csv", filetypes = [("CSV", ".csv")])
        l = list(x)
        self.inputFilesBE.set(",".join(l))

    def templFileSetter(self):
        x = askopenfilename(title = "Template Datei auswählen", defaultextension = ".xml", filetypes = [("XML", ".xml")])
        self.templateBE.set(x)

    def starten(self):
        eb = Ebics(self.inputFilesBE.get(),
                self.outputLE.get(),
                self.betragLE.get(),
                "," if self.sepOM.get() == "Komma" else ";",
                self.zweckLE.get(),
                self.mandatLE.get(),
                self.templateBE.get())
        try:
            eb.createEbicsXml()
            showinfo("Erfolg", "Ausgabe in Datei " + self.outputLE.get() + " erzeugt")
        except Exception as e:
            showerror("Fehler", str(e))



# locale.setlocale(locale.LC_ALL, "de_DE")
locale.setlocale(locale.LC_TIME, "German")
root = Tk()
app = MyApp(root)
app.master.title("ADFC Lastschrift")
app.mainloop()


