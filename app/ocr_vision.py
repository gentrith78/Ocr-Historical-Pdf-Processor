import os
import io

from google.cloud import vision

try:
    from .structured_data import WordData
except:
    from structured_data import WordData

class OcrManager():
    def __init__(self):
        self.base_path = os.path.abspath(os.path.dirname(__file__))
        self._set_env_var()
        self.threshold = 15
    def _get_ocr_data(self, image_path):
        bounds = []
        client = vision.ImageAnnotatorClient()
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        texts = response.text_annotations
        data = []
        for text in texts:
            data.append(text.description)
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        document = response.full_text_annotation
        for page in document.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''
                        for symbol in word.symbols:
                            if not str(symbol.text).isspace() or not str(symbol.text) == '':
                                word_text += symbol.text
                        # word_text += ' '
                        word_obj = WordData(
                            text=word_text,
                            TL=(word.bounding_box.vertices[0].x, word.bounding_box.vertices[0].y),
                            TR=(word.bounding_box.vertices[1].x, word.bounding_box.vertices[1].y)
                        )
                        bounds.append(word_obj)
        return bounds

    def get_lines(self, image_path):
        """Should return a list and each element of this list is a list of
            WordData objects that are sorted into lines based on y coord
        """
        words = self._get_ocr_data(image_path)
        sorted_word_data = sorted(words, key=lambda word: word.TL[1])
        lines = []
        current_line = []
        # Group WordData objects into lines
        for word_data in sorted_word_data:
            if not current_line or (word_data.TL[1] - current_line[-1].TL[1]) < self.threshold:
                current_line.append(word_data)
            else:
                lines.append(current_line)
                current_line = [word_data]
        # Append the last line
        if current_line:
            lines.append(current_line)
        # Sort WordData objects within each line based on X coordinate (TL[0])
        for line in lines:
            line.sort(key=lambda word: word.TL[0])

        return lines

    def _set_env_var(self):
        creds_path = os.path.join(self.base_path,'ocr-python-vision_key.json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(creds_path)