import os
import traceback
import shutil
import subprocess
import xml.etree.ElementTree as ET
import re
from paddleocr import PaddleOCR
from PIL import Image
from pdf2image import convert_from_path
from .restruct import reconstruct
import fitz

# DOC TYPES
IMAGE = 'IMAGE'
READABLE_DOC = 'TEXT'
NONREADABLE_DOC = 'SCAN'
TXT_FILE = 'TXT_FILE'

# EXTENSIONS SUPPORTED
imgExt = ['.png', '.jpg', '.jpeg', '.ppm', '.bmp']
pdfExt = ['.pdf']
txtExt = ['.txt']

class call_ocr():
    def __init__(self, input_path, output_path):
        self.inputpath = input_path
        self.outputpath = output_path

    @property
    def output_path(self):
        output_dir = os.path.join(self.outputpath, os.path.splitext(os.path.basename(self.inputpath))[0])
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        return output_dir
    
    def is_pdf_searchable(input_path,min_searchable_words=30):  

        """
        Check if a PDF is searchable with a minimum number of searchable words.
        """
        page_status = {}
        try:
            doc = fitz.open(input_path)
            total_words = 0
            for i, page in enumerate(doc):
                text = page.get_text("text")
                words = text.split()
                total_words = len(words)
                if total_words >= min_searchable_words:
                    page_status[str(i+1)] = READABLE_DOC
                else:
                    page_status[str(i+1)] = NONREADABLE_DOC
            return page_status

        except Exception as e:
            print(f"Error processing {input_path}: {e}")
            return page_status

    def pdftohtml(self):
        pages_status = {}
        output_path = os.path.join(self.output_path, "XML")
        if os.path.isdir(output_path):
            shutil.rmtree(output_path)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        outpath = os.path.join(output_path, "XML")

        try:
            # command = "pdftohtml -xml -q '" + inputPath + "' '" + outpath + "'"
            # os.system(command)

            command = ["pdftohtml", "-xml", "-q", self.inputpath, outpath]

            try:
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error occurred: {e}")

            dirList = os.listdir(output_path)
            xml = [f for f in dirList if f.lower().endswith(".xml")]
            xmlPath = os.path.join(output_path, xml[0])
            tree = ET.parse(xmlPath)
            doc = tree.getroot()
            text_count = 0

            ratio = 0.0
            for page in doc:
                for i, j in page.attrib.items():
                    # print(i, j, "fdfd")
                    if i == 'number':
                    # if i == 'number' and int(j) == 6:
                    #if int(page.attrib['number']) == 1:
                        page_area = int(page.attrib['width'])*int(page.attrib['height'])

                        for child in page:
                            if child.tag == 'image':
                                image_area =  int(child.attrib['width'])*int(child.attrib['height'])
                                ratio = image_area/page_area
                                #print("image area",child.tag,child.attrib,image_area)
                            if child.tag == 'text':
                                text_count += 1
                        if ratio < 0.125 and text_count >20:
                            pages_status[j] =  READABLE_DOC
                                # return READABLE_DOC, output_path
                        else:
                            pages_status[j] =  NONREADABLE_DOC
                # return NONREADABLE_DOC, output_path
        except Exception as e:
            print("Exception in pdftohtml execution flow", e)
            print(traceback.print_exc())
            pages_status = call_ocr.is_pdf_searchable(self.inputpath)
            print(pages_status, "pages from fitz")
            return pages_status
            
        return pages_status

    def generate_digital_text(self, page_no):
        output_folder = os.path.join(self.output_path, "text_files")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)            
                    
        output=f'{os.path.join(output_folder, os.path.splitext(os.path.basename(self.inputpath))[0])}_page_{page_no}.txt'
        # Construct the pymupdf command
        command = [
            'pymupdf', 'gettext', 
            '-o', output,
            '-nol', '-nof', 
            '-c', '-g', '3', 
            '-e', self.inputpath,
            '-pages', str(page_no)
        ]
        # Run the command
        subprocess.run(command, check=True)   


    def convert_format(input_file, output_file):
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            index = 0  # Initialize the image index
            for line in infile:
                
                word_match = re.search(r'WORD:\s*(.*?)\s*BBOX:', line)
                bbox_match = re.search(r'BBOX:\s*([0-9.]+)\s*([0-9.]+)\s*([0-9.]+)\s*([0-9.]+)', line)
                
                if word_match and bbox_match:
                    word = word_match.group(1).strip()
                    x_min, y_min, x_max, y_max = map(float, bbox_match.groups())
                    
                    # Calculate x, y, w, h
                    x = int(x_min)
                    y = int(y_min)
                    w = int(x_max - x_min)
                    h = int(y_max - y_min)
                    
                    
                    output_line = f"{index}_0.png\t{x} {y} {w} {h}\t{word}\n"
                    outfile.write(output_line)
                    
                    index += 1

    def process_image(self, filepath):
        print(filepath, "scan image file path")
        words = []
        bboxes = []
        try:
            with Image.open(filepath) as img:
                img_width, img_height = img.size

            if not isinstance(filepath, str):
                filepath = str(filepath)

            ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True)
            print(ocr, "loaded")
            result = ocr.ocr(filepath, cls=True)
            print(result, "True")

            output_folder = os.path.join(self.output_path, "text_files")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)


            if result and len(result) > 0:
                file_path = f'{os.path.join(output_folder, os.path.splitext(os.path.basename(filepath))[0])}'
                if os.path.exists(file_path+"_coordinates.txt"):
                    os.remove(file_path+"_coordinates.txt")
                with open(file_path+"_coordinates.txt", 'a') as file:
                    for line in result[0]:
                        bbox, (text, _) = line
                        x_min, y_min = bbox[0]
                        x_max, y_max = bbox[2]
                        file.write(f"WORD:  {text}  BBOX: {x_min} {y_min} {x_max} {y_max}\n")
                    

                call_ocr.convert_format(file_path+"_coordinates.txt", file_path+"_info.txt")   
                reconstruct(file_path+"_info.txt")
            

        except Exception as e:
            print(f"Error processing image: {e}")
            traceback.print_exc()

        return file_path+".txt"

    def convert_pdf_to_images(self):

        # If output_dir is None, use the base name of the PDF file
        output_dir = os.path.join(self.output_path, "pdf_to_img")
        # Convert PDF pages to images
        images = convert_from_path(self.inputpath)

        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save each page as an image in the output directory
        for i, image in enumerate(images):
            output_path = os.path.join(output_dir, f'{os.path.splitext(os.path.basename(self.inputpath))[0]}_page_{i+1}.jpg')
            image.save(output_path, 'JPEG')
        # print(f"Images saved in '{output_dir}' directory with naming format 'filename_1.jpg'")

        # Return the directory where images are saved
        return output_dir
    
    def combine_txt_path(self):
        txtfiles_path = os.path.join(self.output_path, "text_files")
        filename =  os.path.splitext(os.path.basename(self.inputpath))[0]
        output_file = os.path.join(self.output_path, filename+".text")
        with open(output_file, 'w') as file:
            file.write('')
            file.close()
        if os.path.exists(txtfiles_path):
            for file in os.listdir(txtfiles_path):
                if not file.endswith("info.txt") and not file.endswith("coordinates.txt") and file.endswith(".txt"):
                    with open(os.path.join(txtfiles_path, file), 'r') as src, open(output_file, 'a') as dst:
                        content = src.read()
                        # Write content to the destination file
                        dst.write(content)
                        dst.write("")

            return output_file


    def convert_pdf_to_text(self):
        pages_status = self.pdftohtml()
        images_dir = self.convert_pdf_to_images()
        if pages_status:
            if all(status == READABLE_DOC for status in pages_status.values()):
                print("all_pages_digital")
                doc=fitz.open(self.inputpath)
                no_of_page = doc.page_count
                for i in range(1, no_of_page+1):
                    self.generate_digital_text(i)

            else:
                for i, status in pages_status.items():
                    try:
                        if status == READABLE_DOC:
                            self.generate_digital_text(i)
                        elif status ==  NONREADABLE_DOC:
                            self.process_image(os.path.join(images_dir, f"{os.path.splitext(os.path.basename(self.inputpath))[0]}_page_{i}.jpg"))
                    except:
                        traceback.print_exc()
                        pass
        else:
            for i, image in enumerate(os.listdir(images_dir)):
                self.process_image(os.path.join(images_dir, image))
                pages_status[str(i+1)] = NONREADABLE_DOC

        combine_txt = self.combine_txt_path()
        return combine_txt, pages_status


    def ocr_main(self):
        try:

            extension = str((os.path.splitext(os.path.basename(self.inputpath))[-1]).lower())    
            if extension in imgExt:
                return self.process_image(self.inputpath), ""

            elif extension in pdfExt:
                return self.convert_pdf_to_text()  
            
            elif extension in txtExt:
                return self.inputpath, ""
            
            else:
                return "Unsupported File format", ""
        except:
            return "Unsupported File format", ""
