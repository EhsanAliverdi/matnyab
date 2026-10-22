import os,shutil
import re
import threading
import pytesseract
from pdf2image import convert_from_path
from .preprocess import *
import tempfile
import platform
from pathlib import Path
import natsort
from shutil import copyfile
from pathlib import Path
from docx import Document
from docx.shared import Inches


LANGS = "fas"  # Languages for OCR eng+fas
ROOT_FOLDER = os.path.dirname(os.path.dirname(__file__))
#input_data_folder = os.path.join(ROOT_FOLDER, "data")  # Directory of pdf/image files
#print(f'Input Data Directory:\n{self.input_data_folder}')
# OUTPUT_FOLDER = os.path.join(ROOT_FOLDER, "output")  # Directory of ocr'ed images
# print(f'Output Directory:\n{OUTPUT_FOLDER}')



DPI = 200
#TEMP_FOLDER = os.path.join(ROOT_FOLDER, "temp")

FIRST_PAGE = None
LAST_PAGE = None
FORMAT = 'jpg'
THREAD_COUNT = 1
USERPWD = None
USE_CROPBOX = False
STRICT = False
SUPPORTED_IMG_FORMAT = ['.png', '.jpg', '.jpeg', '.tiff']


class ocr:
    
    def __init__(self,input:str, input_type:str, output_folder : str,
                single_file : bool = True, per_page_file : bool = False,
                ms_world_output: bool = True, plain_text_output : bool = True):

        if input_type not in ("FOLDER", "FILE"):
            raise Exception('InvalidInputType: input_type Must be "FOLDER" or "FILE"')

        self.input = input
        self.output_folder = output_folder
        self.single_file = single_file
        self.plain_text_file = plain_text_output
        self.per_page_file = per_page_file
        self.ms_world_output = ms_world_output

        
        self.temp_folder = tempfile.mkdtemp()
        self.temp_image_output_folder = os.path.join(self.temp_folder, "temp_image")
        self.temp_tiff_folder = os.path.join(self.temp_folder, "temp_tiff")
        self.temp_data_folder = os.path.join(self.temp_folder, "temp_data")
        self.temp_text_folder = os.path.join(self.temp_folder, "temp_text")
        self.temp_processed_images = os.path.join(self.temp_folder, "temp_processed_image")
        temp_folders = [self.temp_folder, self.temp_image_output_folder, self.temp_tiff_folder,
                        self.temp_data_folder, self.temp_text_folder, self.temp_processed_images]

        for f in temp_folders:
            Path(f).mkdir(parents=True, exist_ok=True)

        #Move input(s) to temp data folder
        if input_type == "FOLDER":
            for filename in os.listdir(self.input):
                fullName = os.path.join(self.input, filename)
                shutil.copy2(fullName, self.temp_data_folder)
        if input_type == "FILE": 
            shutil.copy2(self.input, self.temp_data_folder)
        

        



            
                # for filename in os.listdir(self.temp_image_output_folder):
                #     file_path = os.path.join(self.temp_image_output_folder, filename)
                #     try:
                #         if os.path.isfile(file_path) or os.path.islink(file_path):
                #             os.unlink(file_path)
                #         elif os.path.isdir(file_path):
                #             shutil.rmtree(file_path)
                #     except Exception as e:
                #         print('Failed to delete %s. Reason: %s' % (file_path, e))

    

    def main(self, progress_callback):
        if (self.ms_world_output or self.plain_text_file) and (self.single_file or self.per_page_file):
            threads = []
            threads.append(threading.Thread(target=self._convertPdfToImg))
            threads.append(threading.Thread(target=self._moveImagesToTempTiff))
            threads.append(threading.Thread(target=self._convertImageToText))
            self.progress_callback = progress_callback
            
            for th in threads:
                #th.daemon = True
                th.start()
                th.join()
            
            self._create_text_output()
            self._create_msworrd_output()


        # Evaluate the result based on Levenshtein distance
        # evaluate_result(text)


        print('------------------DONE-------------------')
    
    def _convertImageToText(self):
        for filename in os.listdir(self.temp_processed_images):
            if filename.endswith(tuple(SUPPORTED_IMG_FORMAT)):
                print(f'Creating Text File from :{filename}')
                fileAddress = os.path.join(self.temp_processed_images, filename)
                img = preprocess().process_image(fileAddress)

                # Recognize the text as string in image using pytesserct
                config = ''
                print(f'\tRecognize the text for :{filename}')
                text = str(pytesseract.image_to_string(img, lang=LANGS, config=config))

                # Remove empty lines of text - s.strip() removes lines with spaces
                text = os.linesep.join([s for s in text.splitlines() if s.strip()])

                # Creating a text file to write the output
                print(f'\tCreating a text file for :{filename}')
                outfile = os.path.join(self.temp_text_folder, "out_" + os.path.splitext(filename)[0] + ".txt")
                with open(outfile, 'w', encoding="utf-8") as text_file:
                    print(text, file=text_file)


    
    def _moveImagesToTempTiff(self):
        for filename in os.listdir(self.temp_data_folder):
            if filename.endswith(tuple(SUPPORTED_IMG_FORMAT)):
                fullName = os.path.join(self.temp_data_folder, filename)
                shutil.copy2(fullName, self.temp_tiff_folder)
        for filename in os.listdir(self.temp_tiff_folder):
            if filename.endswith(tuple(SUPPORTED_IMG_FORMAT)):
                fullName = os.path.join(self.temp_tiff_folder, filename)
                shutil.copy2(fullName, self.temp_processed_images)
        
        # # move supported image formats from input to Temp_data folder
        # for filename in os.listdir(self.input_data_folder):
        #     if filename.endswith(tuple(SUPPORTED_IMG_FORMAT)):
        #         fullName = os.path.join(self.input_data_folder, filename)
        #         shutil.copy2(fullName, self.temp_data_folder)
        # # move supported image formats from temp_tiff to Temp_data folder
        # for filename in os.listdir(self.temp_tiff_folder):
        #     if filename.endswith(tuple(SUPPORTED_IMG_FORMAT)):
        #         fullName = os.path.join(self.temp_tiff_folder, filename)
        #         shutil.copy2(fullName, self.temp_data_folder)


    def _convertPdfToImg(self):
        for filename in os.listdir(self.temp_data_folder):
            # Convert pdf to image files
            if filename.endswith('.pdf'):
                print(f'Converting pdf {filename} to image')
                fullName = os.path.join(self.temp_data_folder, filename)
                pages = convert_from_path(fullName, dpi=DPI, output_folder=self.temp_image_output_folder, first_page=FIRST_PAGE, last_page=LAST_PAGE, fmt=FORMAT, thread_count=THREAD_COUNT, userpw=USERPWD, use_cropbox=USE_CROPBOX, strict=STRICT)

                #pages = convert_from_path(fullName, 500)
                image_counter = 1
                print(filename)
                pdf_name = str(os.path.splitext(fullName)[0]).split("\\")[-1]
                
                total =len(list(pages))
                for page in pages:
                    print(f'\tConverting page {image_counter} to TIFF')
                    image_name = self.temp_tiff_folder +'\\'+ pdf_name + '___PAGE___' + str(image_counter) + '.tiff'
                    #image_name = os.path.splitext(fullName)[0] + '_' + str(image_counter) + '.tiff'
                    page.save(image_name, format='TIFF')
                    self.progress_callback.emit(image_counter*100/total)
                    image_counter += 1
        return True


    def _create_text_output(self):
        #Organise Output files created in temp folder and put them in a dictionary
        files = list(os.listdir(self.temp_text_folder))
        files = natsort.natsorted(files, reverse=False)
        input_files = {}
        for name in files:
            try:
                key = str(name).split('___PAGE___')[0]
            except:
                key = str(name).split('.')[0]
            
            if not key in input_files:
                input_files[key] = [name]
            else:
                input_files[key].append(name)
        
        #create a single output if user wants single file
        if self.single_file:
            for key, value in input_files.items():
                with open(self.output_folder + '/' + key + '_output.txt', 'w', encoding="utf-8") as outfile:
                    for filename in value:
                        print(f'Merging file {filename}')
                        fileAddress = os.path.join(self.temp_text_folder, filename)
                        with open(fileAddress, 'r', encoding="utf-8") as infile:
                            for line in infile:
                                outfile.write(line)
                            try:
                                file = str(filename).split('.')[0]
                                page_number = str(file).split('___PAGE___')[1]
                                outfile.write(f'------------------  PAGE {str(page_number)}  ------------------\n')
                            except:
                                outfile.write('------------------  PAGE ????  ------------------\n')
        #create a file for each page if user wants file per page
        if self.per_page_file:
            for key, value in input_files.items():
                for filename in value:
                    print(f'moving file from temp to output {filename}')
                    src = os.path.join(self.temp_text_folder, filename)
                    dst = str(self.output_folder + '/' + key).replace('.txt', '') + ' Plain Text/'
                    Path(dst).mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(src, dst)



    def _create_msworrd_output(self):
        #Organise Output files created in temp folder and put them in a dictionary
        files = list(os.listdir(self.temp_text_folder))
        files = natsort.natsorted(files, reverse=False)
        input_files = {}
        for name in files:
            try:
                key = str(name).split('___PAGE___')[0]
            except:
                key = str(name).split('.')[0]
            
            if not key in input_files:
                input_files[key] = [name]
            else:
                input_files[key].append(name)
        #create a single output if user wants single file
        if self.single_file:
            
            for key, value in input_files.items():
                document = Document()
                for filename in value:
                    print(f'Merging file {filename} into ms word')
                    fileAddress = os.path.join(self.temp_text_folder, filename)
                    with open(fileAddress, 'r', encoding="utf-8") as infile:
                        p = document.add_paragraph(infile)
                        # for line in infile:
                        #     p = document.add_paragraph(line)
                    document.add_page_break()
                desfilename = self.output_folder + '/' + key + '_output.docx'
                document.save(desfilename)
        
        if self.per_page_file:
            for key, value in input_files.items():
                for filename in value:
                    document = Document()
                    dst = str(self.output_folder + '/' + key).replace('.txt', '') + ' MS Word/'
                    print(f'Creating Ms word {filename}')
                    fileAddress = os.path.join(self.temp_text_folder, filename)
                    with open(fileAddress, 'r', encoding="utf-8") as infile:
                        p = document.add_paragraph(infile)
                        dst = str(self.output_folder + '/' + key).replace('.txt', '') + ' MS Word/'
                        fileAddress = dst + str(filename).replace(".txt", '') + '.docx'
                        Path(dst).mkdir(parents=True, exist_ok=True)
                        document.save(fileAddress)


        

        pass


    # def evaluate_result(text):
    #     import docx2txt
    #     import Levenshtein
    #     original_text = docx2txt.process(os.path.join(self.input_data_folder, "original.docx"))
    #     original_text = os.linesep.join([s for s in original_text.splitlines() if s.strip()])

    #     text = re.sub(r'[|]', '', text)

    #     distance = Levenshtein.distance(original_text, text)
    #     print(distance)


if __name__ == "__main__":
    ocr().main()
