import os
import uuid
import pickle

from pathlib import Path

import fitz
from PIL import Image

try:
    from .utils import DfConvert
    from .ocr_vision import OcrManager
    from .structured_data import  Property
    from .property_parser import PropertyParser
except:
    from utils import DfConvert
    from ocr_vision import OcrManager
    from structured_data import Property
    from property_parser import PropertyParser

class Parser(OcrManager, DfConvert):
    def __init__(self, pdf_path):
        OcrManager.__init__(self)
        DfConvert.__init__(self)
        self.pdf_path = pdf_path
        self.base_path = os.path.abspath(os.path.dirname(__file__))

    def process(self):
        doc = fitz.open(self.pdf_path)
        for page_nr, page in enumerate(doc):
            #save page as image
            if page_nr != 0:
                # continue
                pass
            page_as_image_path = self._save_image(page)
            #get lines
            lines = self.get_lines(page_as_image_path)
            pkl_path = Path(self.base_path).joinpath(f"page_{page_nr + 1}.pkl")
            with open(str(pkl_path), 'wb') as file:
                pickle.dump(lines,file)
            # lines = self.__openWithpickle(page_nr)
            print(f"processing page", page_nr+1)
            #get properties
            try:
                properties = self._get_properties(lines, page_nr)
            except Exception as e:
                print(str(e))
                continue
            #save to csv
            self._save_to_csv(properties, page_nr)
            #rmv image
            os.remove(page_as_image_path)
    def __openWithpickle(self,page_nr):
        pkl_path = Path(self.base_path).joinpath(f"page_{page_nr + 1}.pkl")
        with open(str(pkl_path), 'rb') as file:
            return pickle.load(file)
    def _get_properties(self, lines, page_nr):
        instance = PropertyParser(lines, page_nr+1)
        instance.process()
        return instance.parcels
    def _save_to_csv(self, properties, page_nr):
        self.write_to_csv(properties, page_nr + 1)
    def _save_image(self,page):
        img_path = os.path.join(self.base_path,'active',f"{uuid.uuid4()}.jpg")
        dpi = 300
        zoom = dpi / 72
        magnify = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=magnify)
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        img.save(img_path)
        img.close()
        return img_path


if __name__ == '__main__':
    path_to_pdf = r'C:\Users\Gigi\Desktop\HistoricalPdfScraper\test_files\AHA 1964-21-150.pdf'
    proc = Parser(path_to_pdf)
    proc.process()