import os

import pandas as pd
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
from difflib import SequenceMatcher

def write_page(ocr_data, page_nr):
    merged_text = ''
    for l in ocr_data:
        merged_text += f" {l.text}"
    with open(f"page_{page_nr}.txt", 'w', encoding="utf-8") as file:
        file.write(merged_text)

def ensure_active_dir():
    current_path = os.path.abspath(os.path.dirname(__file__))
    if not os.path.exists(os.path.join(current_path,'active')):
        os.mkdir(os.path.join(current_path,'active'))

def rmv_bad_chars(word:str):
    # TODO rmv these chars: â€¦â€¦ â€¦  â€“ â€¦ â€“
    word.text = word.text.replace('â€“', '-').replace('–','-').replace('â€¦','...')
    return word

def similarity(first_string, second_string):
    return SequenceMatcher(None, first_string, second_string).ratio()


class DfConvert():
    def __init__(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))

    def write_to_csv(self, properties, page_nr):
        csv_name = f"Page {page_nr} -- {datetime.strftime(datetime.now(), '%d_%m-%H_%M')}.csv"
        csv_path = str(Path(self.base_dir).joinpath('output').joinpath(csv_name))
        dataframes = []
        for prop in properties:
            dataframes.append(pd.DataFrame(self._serialiseProp(prop)))
        pd.concat(dataframes).to_csv(csv_path,index=False)

    def _serialiseProp(self, prop):
        prop = asdict(prop)
        for key, val in prop.items():
            prop[key] = [val]
        return prop
if __name__ == '__main__':
    print(datetime.strftime(datetime.now(), '%d_%m-%H_%M'))
