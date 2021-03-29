import cv2
import pytesseract
from pytesseract import Output
import pandas as pd

class OpenCv:
    def __init__(self, url):
        self.image_url = url
        self.image_path = self.download(url = url)

    def process(self, image_path = None):
        if image_path is None:
            image_path = self.image_path
        img = cv2.imread(image_path)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        custom_config = r'-l eng --oem 1 --psm 6 '
        d = pytesseract.image_to_data(thresh, config=custom_config, output_type=Output.DICT)
        df = pd.DataFrame(d)

        df1 = df[(df.conf != '-1') & (df.text != ' ') & (df.text != '')]
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        sorted_blocks = df1.groupby('block_num').first().sort_values('top').index.tolist()
        for block in sorted_blocks:
            curr = df1[df1['block_num'] == block]
            sel = curr[curr.text.str.len() > 3]
            # sel = curr
            char_w = (sel.width / sel.text.str.len()).mean()
            prev_par, prev_line, prev_left = 0, 0, 0
            text = ''
            for ix, ln in curr.iterrows():
                # add new line when necessary
                if prev_par != ln['par_num']:
                    text += '\n'
                    prev_par = ln['par_num']
                    prev_line = ln['line_num']
                    prev_left = 0
                elif prev_line != ln['line_num']:
                    text += '\n'
                    prev_line = ln['line_num']
                    prev_left = 0

                added = 0  # num of spaces that should be added
                if ln['left'] / char_w > prev_left + 1:
                    added = int((ln['left']) / char_w) - prev_left
                    text += ' ' * added
                text += ln['text'] + ' '
                prev_left += len(ln['text']) + added + 1
            text += '\n'
        self.result = text
        self.check_words()
        self.bad_words()
        self.datasetes()
        self.keys()
        self.send()
        return text

        
    def download(self, url = None):
        if url is None:
            url = self.url
        import os
        import requests

        page = requests.get(url)

        f_ext = os.path.splitext(url)[-1]
        import time
        ts = time.time()

        f_name = 'images/img-' + str(ts) + '{}'.format(f_ext)
        with open(f_name, 'wb') as f:
            f.write(page.content)
        self.donwloaded_image = f_name
        return f_name

    def check_words(self):
        text = (self.result.split())
        # # Removeing words for unknown reasons

        # keyword_list = ['Specific Gravity','Semi Turbid','Epithelial cells/Lpf','Amorphus urate Few','RBCih  pf','RBC/h p f','Ep Celis /h.p.f','Semi clear','Yeltow','Blood (Hemoglobin)','W.B.C    /h.p.f','R.B.C    —/h.p.f','R.B.C    /h.p.f','Ep.Cells /h.p.f','Bacteria /h.p.f','Crystals /h.p.f','Casts    /h.p.f','Mucus    /h.p.f','Spore of fungi','*Positive 2+','RBCihPf','WECih.pt',"WBCthpr","RBCApfe","Yeutow","Giucose"]
        # matching_list = ['SpecificGravity','SemiTurbid','EpithelialCells/Lpf','AmorphusUrateFew','RBCihPf','RBC/hpf','EpCelis/h.p.f','SemiClear','yellow','Blood(Hemoglobin)','W.B.C/h.p.f','R.B.C/h.p.f','R.B.C/h.p.f','Ep.Cells/h.p.f','Bacteria/h.p.f','Crystals/h.p.f','Casts/h.p.f','Mucus/h.p.f','SporeOfFungi','*Positive2+','RBC/h.p.f','WBC/h.p.f',"WBC/hpf","RBC/hpf","Yellow","Glucose"]
        # for i,item in enumerate(keyword_list):
        #     if item in text:
        #         text = item.replace(item , matching_list[i])
        self.result = text
        return text
        
    def bad_words(self):
        text = self.result
        bad_chars = ["`",
                    "~",
                    "!",
                    "@",
                    "#",
                    "$",
                    "%",
                    "^",
                    "&",
                    "_",
                    "__",
                    "|",
                    "—",
                    "Urine Analysis",
                    "Macroscopy",
                    "Microscopy",
                    "Test",
                    "Result",
                    "Unit",
                    "Reference value",
                    "Analysis",
                    "analysis",
                    "Urinalysis",
                    "So",
                    "‘",
                    "Urine",
                    "Resear",
                    "=",
                    ":",
                    "Sfacroscopy",
                    "Macroscopic",
                    "Microscopic",
                    "eS",
                    "Micrnscopy",
                    "‘"]


        for v,x in enumerate(text):
            for u,y in enumerate(bad_chars):
                text[v] = text[v].replace(y, '')

        for l,k in enumerate(text):
            if k == '':
                del text[l]


        while '' in text:
            text.remove('')


        x = ['.','-','|','__','_','`','~','.-','-.']

        for x in text:
            if len(x) == 1 and not x.isdigit():
                text.remove(x)
        self.result = text
        return text

    def find_similar(self, search_for, dataset):
        res = []
        from rapidfuzz import fuzz
        import operator
        for data in dataset:
            res.append(fuzz.ratio(search_for, data))
        i, v = max(enumerate(res), key=operator.itemgetter(1))
        yield dataset[i]
        yield v

    def datasetes(self):
        text = self.result
        dataset = [ "Appereance",
                    "Color",
                    "Specifie Gravity",
                    "PH",
                    "Protein",
                    "Glucose",
                    "Ketons",
                    "Blood",
                    "Bilirubin",
                    "Urobilinogen",
                    "Nitrite",
                    "RBC/hpf",
                    "WBC/hpf",
                    "Epithelial cells/Lpf",
                    "EC/Lpf",
                    "Bacteria",
                    "Casts",
                    "Mucous",
                    "Crystals",
                    "Blood(Hemoglobin)",
                    "Bacteria/hpf",
                    "Ep.Cells",
                    "Spore of fungi",
                    "Negative",
                    "Pos(+)",
                    "Positive",
                    "(Few)",
                    "Few",
                    "WBC/h.p.f",
                    "RBC/h.p.f",
                    "Ep Cells/ h.p.f",
                    "Ep Cells/h.p.f",
                    "pH",
                    "WBC/ h.p.f",
                    "RBC/ h.p.f",
                    "Nitrite",
                    "R.B.C/h.p.f",
                    "W.B.C/h.p.f",
                    "Ep.Cells/ h.p.f",
                    "yellow",
                    "Yellow"]

        key_list = []
        value_list = []
        allowed_accurancy = 75
        for i, t in enumerate(text):    
            if i%2 == 0:
                word, accuracy = self.find_similar(t, dataset)
                if accuracy > allowed_accurancy:
                    text[i] = word
                    key_list.append(t)
            else:
                value_list.append(t)
        self.key_list = key_list
        self.value_list = value_list
        return self

    def keys(self):
        text = self.result
        ql = []
        c = 0
        for item in self.key_list:
            try:
                q = {
                    "key":self.key_list[c],
                    "value":self.value_list[c]
                }
                c += 1
                ql.append(q)
            except IndexError:
                continue
        self.json_ready = ql

    def send(self):
        import json
        requestJson = json.dumps(self.json_ready)
        print(requestJson)