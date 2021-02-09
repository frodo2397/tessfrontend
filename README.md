# David's Python Tesseract-OCR frontend for Windows and Linux

This is a frontend that provides a graphical user interface and easy parallelization for Tesseract-OCR 4. You can use it to batch-process multiple PDF or TIFF documents without writing any code, in whichever installed language you choose. It takes an image (or multiple images) as input, and outputs a text file with the machine-read text.

## History and Use Cases:

I created this for for a research project in which I needed to
automate reading and information extraction of a large historical
[French-language document](https://gallica.bnf.fr/ark:/12148/bpt6k5499951n/f17.item).  This was technically challenging for
the OCR side, since the document had been printed with a very small
font.  A human can read the resulting scan with some effort, but all
existing OCR tools that I checked had a fairly high error rate.

In the end I needed a tool that would

1) Make it easy to set the many parameters that tesseract needs to get
   best results.
   
2) Split up a large source PDF file into individual images for
   processing (Tesseract works on images, not PDFs).

3) Apply threshold or blur preprocessing steps to images
   In some cases this can significantly improve accuracy.

4) Execute many  Tesseract OCR processes in parallel.  Even on a 6 core/12
   thread processor, reading the entire file took many hours.

5) Allow a reproducible workflow.  For a publication, it is best if
  other investigators can reproduce your results.  Once the parameters
  are selected in the GUI, the main process creates a script which can
  be run immediately. (However, the script is not saved automatically at 
  this time, so be sure to copy from the terminal if you need this.) 

And, since getting a good OCR processing flow takes some
experimentation, it had to be easy to use and flexible for both
initial experimentation and then the final production runs.

The tool in this directory does all this and more.  I am making it
available in the hopes that others might find it useful.  Also, if you
are in the process of evaluating different tools for a project (as I
was), my hope is tha this project provides a quicker learning curve to
getting tesseract up and running.

## Architecture Overview:

* ocr-gui.py  makes it easy to choose parameters (e.g., file selection), 
which are then fed into ocr2.py. It will run the script multiple times if
given multiple files, but it will not run multiple files in parallel (only
single file at a time, multiple pages in parallel).

* ocr-gui.py just creates a line with parameters for ocr2.py. Thus, behavior
is repeatable if you record the scripts created in terminal, but you don't
have to remember which command line options do what.

* ocr2.py spawns multiple instances of tesseract to process the pages of a
multipage file in parallel. It outputs text files only for now (if different
output is needed, the script may be modifiable for that purpose).

* Each instance of tesseract uses 2-3 threads on average to process an image or 
a single page of a PDF or TIFF document.

## Installation

You will need to have Python 3 installed. 

This frontend integrates a number of libraries and tools in order to
get the desired functionality.  In order to use this project, you will
first need to install:

* Tesseract itself, also any needed language files.
* Python3 - will  already be  installed on many systems.
* pip - an internal package manager for Python.  Several of the
  libraries needed are available for installation with pip.

Then install the dependencies listed below.

### Dependencies

Install the following dependencies with pip or conda before using the program.

1) PIL
2) fitz
3) PyPDF2
4) pytesseract
5) cv2

### Installation on debian-based systems.

Tested recently on a Raspberry Pi.  (Not a recommended OCR system, but 
a convenient blank canvas for testing the install.)  (In progress ...)

To install Tesseract, you will need to run: 
sudo apt install tesseract-ocr

## Running the program

### Ubuntu:

The program can be run by typing into terminal (opened into main directory):

python3 tesseract-python/ocr-gui.py

### Windows:

You may need to reset the tesseract directory if it is not working; change it to the correct directory on the following line of ocr2.py: 
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

Then save the file and open a CMD or powershell window. Navigate to the correct directory, then type:

python tesseract-python/ocr-gui.py

## Using the interface:

### 1) The first option opens a file chooser. You can use the Shift or Ctrl keys to select multiple image files on which to run the script.

Supported file types are PDF, JPG, TIFF, BMP, and PNG. 

### 2) The second option allows you to select two types of preprocessing. These were based on a tutorial by Adrian Rosebrock at [PyImageSearch](https://www.pyimagesearch.com/).

The first type of preprocessing is threshold. It makes the image binary (black and white), which can make it easier for tesseract to process grayscale scanned pages. 

The second type is blur. It slightly blurs the image before sending it to tesseract. That can make it easier to process images with very noisy backgrounds. 

Finally, you can turn off all preprocessing.

### 3) This option allows you to select the language. 

To install languages in tesseract (or see which are included by default), please see the [tesseract documentation](https://github.com/tesseract-ocr/tessdoc/blob/master/Installation.md).

You can even create your own tesseract language models by training the algorithm on data from your specific document. (This helped me improve accuracy significantly.)

### 4) Remove single line breaks from output:
Turn this on if you would prefer not to have line breaks at the end of each line. Warning: tesseract's handling of line breaks can be idiosyncratic depending on the document; it is often best to leave this off if you are doing achine parsing later.  

### 5) Number of pages to process at once:
The script can process different pages (in multipage PDF or TIFF files) in parallel using multiple CPU cores. In general, I would recommend setting this number to about half the number of threads of your CPU if you would like to efficiently process multiple files in parallel, as each tesseract instance seems to use 2-3 threads.

E.g., Intel Xeon X5660 -> 6 cores with 2 threads per core -> 6 pages processed at once.
Intel i7 3770k -> 4 cores with 2 threads per core -> 4 pages processed at once.

### 6) PDF quality factor: 
A multiplier for the page resolution at which it is processed. Try higher numbers if you are not getting accurate results from Tesseract, or lower numbers if it is too slow.

### 7) Python command:
either python (usually on windows) or python3 (usually on linux)

## Progress and Output

### Terminal window

Progress is generally shown in the terminal window after the script starts, but a window will pop up in the GUI when it is done.

### Output location

By default, output text files are stored in output/language/documentname pagenumber.txt

The files marked complete include all pages in one text file.

