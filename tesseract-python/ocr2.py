# USAGE
# python ocr.py --image images/example_01.png 
# python ocr.py --image images/example_02.png  --preprocess blur

# import the necessary packages
from PIL import Image
import fitz 
from PyPDF2 import PdfFileWriter, PdfFileReader
import pytesseract
import argparse
import cv2
import os
import re
from pathlib import Path
import concurrent.futures

#windows only (comment out if on linux)
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True,
    help = "path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type = str, default = "thresh",
    help = "type of preprocessing to be done")
ap.add_argument("-l", "--lang", type = str, default = "fra",
    help = "language to use -- traineddata file in /usr/share/tesseract-ocr/4.00/tessdata (ubuntu) or C:/Program Files/Tesseract-OCR/tessdata (windows)")
ap.add_argument("-s", "--postprocess", type = str, default = "True",
    required = False, help = "Remove single line breaks from paragraphs?")
ap.add_argument("-b", "--batch", type = int, default = 6, required=False, help = "number of pages to process at a time")
ap.add_argument("-z", "--zoom", type = int, default = 8, required=False, help = "(PDF only) zoom factor; higher will be slower but give better results")
args = vars(ap.parse_args())
batch = args["batch"]
zoomFactor = args["zoom"]
trainedData = args["lang"]
#converts string values ('yes' 'false', etc) to True/False
def str2bool(v):
    if isinstance(v, bool):
         return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
postprocess = str2bool(args["postprocess"])

#This method processes the image filenames in the files list by creating threads "lambdas" for 
#the multiprocessing threadpool to work through
#this works per page.
def process_images(files, startIndex):
    index = startIndex  
    with concurrent.futures.ThreadPoolExecutor() as executor:
        lambdas = []
        for file in files:
            print (output_file[1:] + ": processing page ", index+1)
            lambdas.append(executor.submit(process_lambda, file, index, args, output_file))
            index += 1          
        index = startIndex
        for myLambda in lambdas:
            lambdaString = myLambda.result()

            #output filename for this page: output/language/filename_pagenumber
            outputStr = "output/" + trainedData + output_file + "_" + str(index + 1) + ".txt"
            
            os.makedirs(os.path.dirname(outputStr), exist_ok = True)

            with open(outputStr, 'w', encoding='UTF-8') as write_file:
                print(output_file[1:] + ": writing output ", index + 1)
                write_file.write(lambdaString)
                write_file.close()

            #write complete file with all pages
            with open("output/" + trainedData + output_file + "_complete.txt", 'a', encoding = 'UTF-8') as complete_file:
                complete_file.write(lambdaString)
                complete_file.close()
            index += 1

#for each individual page, create temporary processed images, run them through tesseract, then remove them
def process_lambda(file, index, args, output_file):
    image = cv2.imread(file)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #cv2.imshow("Image", gray)

    # check to see if we should apply thresholding to preprocess the
    # image
    if args["preprocess"] == "thresh":
        gray = cv2.threshold(gray, 0, 255,
            cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # make a check to see if median blurring should be done to remove
    # noise
    elif args["preprocess"] == "blur":
        gray = cv2.medianBlur(gray, 3)

    # write the grayscale image to disk as a temporary file so we can
    # apply OCR to it

    filename = "processed" + str(index) + ".tif"
    cv2.imwrite(filename, gray)
    myString = (pytesseract.image_to_string(filename, lang = trainedData))
    os.remove(filename)

    if postprocess == True:
        #remove line breaks using regex
        myString = re.sub(r"(?<!\n)\n(?!\n)", " ", myString)

    return myString


if __name__=="__main__":
    #here I handle differnt argument types (PDF, TIFF, JPG, etc) and multiple selected images
    dotLoc = args["image"].rfind('.')
    slashLoc = args["image"].rfind('/')
    if (slashLoc == -1):
        slashLoc = args["image"].rfind('\\')
    if (slashLoc == -1):
        slashLoc = 0
    imgType = args["image"][dotLoc:]
    output_file = args["image"][slashLoc:dotLoc]
    print("image type: ", imgType)

    img = args["image"]
    images = []
    #pdf: multithreaded by page
    if (imgType == ".pdf"):
        inputpdf = fitz.open(img)
        maxPages = inputpdf.pageCount
        i = 0
        while i <= maxPages:
            files = []
            for x in range (i, min(maxPages, i + batch)):
                print(output_file[1:] + ": loading page %s of %s" % (x + 1, maxPages))
                page = inputpdf.loadPage(x)
                zoom = zoomFactor    # zoom factor
                mat = fitz.Matrix(zoom, zoom)
                pix = page.getPixmap(matrix = mat)
                file = str('pixmap'+str(x) + '.tif')
                files.append(file)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(file, 'TIFF')

            process_images(files, i)
            for file in files:
                filename = file.format(os.getpid())
                os.remove(file)
            i += batch
    #tiff: multithreaded by page
    elif (imgType == ".tif") or (imgType == ".tiff"):
        tiffImg = Image.open(args["image"])
        maxPages = tiffImg.n_frames
        
        i = 0
        while i < maxPages:
            files = []
            for x in range (i, min(maxPages, i + batch)):
                print(output_file[1:] + ": loading page %s of %s" % (x + 1, maxPages))
                tiffImg.seek(x)
                file = str(x) + '.tif'
                tiffImg.save(file, 'TIFF')
                files.append(file)

            process_images(files, i)
            for file in files:
                filename = file.format(os.getpid())
                os.remove(file)
            i += batch
    #other image type: single image at a time.
    else:
        files = []
        files.append(args["image"])
        process_images(files, 0)