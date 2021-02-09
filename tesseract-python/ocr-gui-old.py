from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import StringVar
from tkinter.ttk import Combobox
import os

#simple tkinter GUI frontend for tesseract. See readme for more details. 

#run button clicked, run ocr2.py script for each selected image
def runClicked():
	runStrings = []
	for file in window.filepath:

		#output is ultimately a terminal command, gotten from all gui elements.
		runString = pycmd.get()+" ocr2.py -i \""+file+"\" -p "+preprocCombo.get()+" -l "+lang.get()+" -s "+lbCombo.get()+" -b "+ pgCombo.get() + " -z "+ qCombo.get()
		runStrings.append(runString)

		if (file == "Choose..." or file == ""):
			messagebox.showerror("Error", "Please choose file(s) on which to run the script.")
			return

	result = messagebox.askyesno("Ok to execute these "+str(len(runStrings))+" scripts?", runStrings[0])	
	if (result != True):
		print("Canceled.")
		return

	for i in range (0, len(runStrings)):
		runString = runStrings[i]
		window.title("David's Tesseract-OCR frontend : Script "+str(i+1)+" of "+str(len(runStrings))+" is running.")
		print(">>"+runString)
		os.system(runString)

	window.title("David's Tesseract-OCR frontend")
	print("done")
	messagebox.showwarning("Message", "The scripts are complete.")




window = Tk()
window.title("David's Tesseract-OCR frontend")
window.geometry('700x300')
window.configure(bg='dark grey')
window.filepath = ("Choose...",)


def fileClicked():
	window.filepath = filedialog.askopenfilenames(initialdir="images", title = "Select image file or folder of images",filetypes = (("image files","*.jpg *.png *.tif *.tiff *.bmp *.pdf *.gif"),("all files","*.*")))
	print(window.filepath)

	file_text.set(str(str(len(window.filepath))+": "+window.filepath[0][window.filepath[0].rfind("/")+1:])[:15])


#simple visual arrangement of different types of boxes
lbl = Label(window, text="  Fill out the entries below to run tesseract.    ", bg="dark grey", fg="black", font=("Arial Bold", 15))
lbl.grid(column=0, row=0, columnspan = 2)

lbl2 = Label(window, text="  Image file, PDF, or multipage TIFF file to OCR:    ", bg="dark grey", fg="dark blue", font=("Arial", 12), anchor=E)
lbl2.grid(column=0, row=1, sticky=W+E)

file_text = StringVar()


filebtn = Button(window, textvariable=file_text, command = fileClicked, bg = "white", font=("Arial", 12), width=15)
filebtn.grid(column=1, row=1, sticky=W)
file_text.set(window.filepath)

lbl3 = Label(window, text="  Type of preprocessing to be done (threshold or blur):    ", bg="light grey", fg="dark blue", font=("Arial", 12), anchor=E)
lbl3.grid(column=0, row=2, sticky=W+E)
preprocCombo = Combobox(window, state="readonly", values = ("thresh", "blur", "none"), font=("Arial", 12), width=14)
preprocCombo.current(0)
preprocCombo.grid(column=1, row=2, sticky=W)

lbl4 = Label(window, text="  Language of document (e.g., eng or fra):    ", bg="dark grey", fg="dark blue", font=("Arial", 12), anchor=E)
lbl4.grid(column=0, row=3, sticky=W+E)
lang = Entry(window,width=16, font=("Arial", 12))
lang.grid(column=1, row=3, sticky=W)
lang.insert(0, "fra")

lbl5 = Label(window, text="  Remove single line breaks from output?    ", bg="light grey", fg="dark blue", font=("Arial", 12), anchor=E)
lbl5.grid(column=0, row=4, sticky=W+E)

lbCombo = Combobox(window, state="readonly", values = ("Yes", "No"), font=("Arial", 12), width=14)
lbCombo.current(1)
lbCombo.grid(column=1, row=4, sticky=W)


lbl6 = Label(window, text="  Number of pages to process at once (multi-page PDF or TIFF only):    ", bg="dark grey", fg="dark blue", font=("Arial", 12), anchor=E)
lbl6.grid(column=0, row=5, sticky=W+E)


pgCombo = Combobox(window, state="readonly", values = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), font=("Arial", 12), width=14)
pgCombo.current(5)
pgCombo.grid(column=1, row=5, sticky=W)

lbl7 = Label(window, text="  PDF quality factor (leave at default if you aren't sure):    ", bg="light grey", fg="dark blue", font=("Arial", 12), anchor=E)
lbl7.grid(column=0, row=6, sticky=W+E)
qCombo = Combobox(window, state="readonly", values = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), font=("Arial", 12), width=14)
qCombo.current(3)
qCombo.grid(column=1, row=6, sticky=W)

lbl7 = Label(window, text="  Python command:    ", bg="dark grey", fg="dark blue", font=("Arial", 12), anchor=E)
lbl7.grid(column=0, row=7, sticky=W+E)
pycmd = Entry(window,width=16, font=("Arial", 12))
pycmd.grid(column=1, row=7, sticky=W)
pycmd.insert(0, "python3")

lbl9 = Label(window, text="  ", bg="dark grey", fg="dark blue", font=("Arial", 12), anchor=E)
lbl9.grid(column=0, row=8, sticky=W+E)
canvas = Canvas(window, width=800, height=500)



imagetest = PhotoImage(file="ui/execbtn.png")
canvas.create_image(400, 50, image=imagetest)


btn = Button(window, text="Run Tesseract Command", command = runClicked, bg = "dark grey", image = imagetest)
btn.grid(column=0, row = 9, columnspan=2)
#done with gui
window.mainloop()

