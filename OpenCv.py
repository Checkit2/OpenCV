import cv2
import pytesseract
from pytesseract import Output
import pandas as pd

class OpenCv:
    def __init__(self, url = None):
        if url is not None:
            self.image_url = url
            self.image_path = self.download(url = url)
        self.image_url = None
        self.image_path = None

    def process(self, image_path = None, image_url = None):
        if image_path is None:
            image_path = self.image_path
        if image_url is not None:
            self.image_path = self.download(url = image_url, keep = False)
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
        return self.send()

        
    def download(self, url = None, keep = False):
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
        text = self.result
        # # Removeing words for unknown reasons

        keyword_list = ['Specific Gravity','Semi Turbid','Epithelial cells/Lpf','Amorphus urate Few','RBCih  pf','RBC/h p f','Ep Celis /h.p.f','Semi clear','Yeltow','Blood (Hemoglobin)','W.B.C    /h.p.f','R.B.C    —/h.p.f','R.B.C    /h.p.f','Ep.Cells /h.p.f','Bacteria /h.p.f','Crystals /h.p.f','Casts    /h.p.f','Mucus    /h.p.f','Spore of fungi','*Positive 2+','RBCihPf','WECih.pt',"WBCthpr","RBCApfe","Yeutow","Giucose", "Yeltow"]
        matching_list = ['SpecificGravity','SemiTurbid','EpithelialCells/Lpf','AmorphusUrateFew','RBCihPf','RBC/hpf','EpCelis/h.p.f','SemiClear','yellow','Blood(Hemoglobin)','W.B.C/h.p.f','R.B.C/h.p.f','R.B.C/h.p.f','Ep.Cells/h.p.f','Bacteria/h.p.f','Crystals/h.p.f','Casts/h.p.f','Mucus/h.p.f','SporeOfFungi','*Positive2+','RBC/h.p.f','WBC/h.p.f',"WBC/hpf","RBC/hpf","Yellow","Glucose"]
        for i,item in enumerate(keyword_list):
            if item in text:
                text = text.replace(item , matching_list[i])
        self.result = (text.split())
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
        # import json
        # requestJson = json.dumps(self.json_ready)
        # print(requestJson)
        
        yield self.key_list
        yield self.value_list
    
    def analysis(self, keys, values):
        value = values
        explain = ""
        for i,item in enumerate(keys):
            if item == 'Color':
                if value[i] == 'Yellow':
                    explain += 'رنگ ادرار مشکلی ندارد'
                    explain += '\n\r'
                    continue
                if value[i] == 'Lightyellow':
                    explain += ' رنگ ادرار مشکلی ندارد اما بهتر است به پزشک مراجعه کنید'
                    explain += '\n\r'
                    continue
                if value[i] == 'Darkyellow':
                    explain += ' رنگ ادرار مشکلی ندارد اما بهتر است به پزشک مراجعه کنید'
                    explain += '\n\r'
                    continue
                if value[i] == 'Red':
                    explain += ' در ادرار شما خون مشاهده شده است لطفا به پزشک مراجعه فرمایید'
                    explain += '\n\r'
                    continue
                if value[i] == 'Orange':
                    explain += ' در ادرار شما کمی مشک در کلیه شما مشاهده شده است لطفا به پزشک مراجعه کنید'
                    explain += '\n\r'
                    continue
                if value[i] == 'Dark' or 'Black':
                    explain += ' در ادرار شما کمی مشک در کلیه شما مشاهده شده است لطفا به پزشک مراجعه کنید'
                    explain += '\n\r'
                    continue                        
                if value[i] == 'White':
                    explain += ' در ادرار شما چرک مشاهده شده است لطفا به پزشک مراجعه کنید'
                    explain += '\n\r'
                    continue
                if value[i] == 'Blue':
                    explain += ' در ادرار شما عفونت سودومونایی مشاهده شده است لطفا به پزشک مراجعه کنید'
                    explain += '\n\r'
                    continue
                if value[i] == 'Green':
                    explain += ' در ادرار شما عفونت سودومونایی مشاهده شده است لطفا به پزشک مراجعه کنید'
                    explain += '\n\r'
                    continue
                if value[i] == 'Brown':
                    explain += ' در ادرار شما نشانه هایی از کم آبی وجود دارد '
                    explain += '\n\r'
                    continue
                if value[i] == 'Paleyellow':
                   explain += ' در ادرار شما رنگدانه اوروکروم مشاهده شده است لطفا به پزشک مراجعه کنید '
                   explain += '\n\r'
                   continue
            if item == 'Appereance':
                if value[i] == 'clear' or 'Clear':
                    explain += ' شفافیت ادرار شما خوب است '
                    explain += '\n\r'
                    continue
                if value[i] == 'SemiClear':
                    explain += ' شفافیت ادرار شما خوب است '
                    explain += '\n\r'
                    continue
                if value[i] == 'Turbid':
                    explain += ' ادرار شما شفاف نیست لطفا به دکتر مراجعه فرمایید '
                    explain += '\n\r'
                    continue
                if value[i] == 'SemiTurbid':
                    explain += ' ادرار شما تقریبا شفاف نیست لطفا به دکتر مراجعه فرمایید '
                    explain += '\n\r'
                    continue
                if value[i] == 'Cloudy' or 'cloudy':
                    explain += ' ادرار شما شفاف نیست لطفا به دکتر مراجعه فرمایید '
                    explain += '\n\r'
                    continue
            if item == 'SpecificGravity' or 'specificgravity':
                if value[i] == '1005' and value[i] < '1025' or value[i] == '1025':
                   explain += ' وزن ادرار شما مشکلی ندارد '
                   explain += '\n\r'
                   continue
                else:
                    explain = ' وزن ادرار شما طبیعی نیست ، لطفا به پزشک مراجعه کنید '
            if item == 'PH' or 'pH':
                if value[i] == '4.5' or value[i] < '8' or value[i] == '8':
                    explain += ' اسید در ادرار شما نرمال است '
                    explain += '\n\r'
                    continue
                elif value[i] > '8':
                    explain += ' اسید در ادرار شما طبیعی نیست ، لطفا به پزشک مراجعه فرمایید '
                    explain += '\n\r'
                    continue
            if item == 'Protein':
                if value[i] == 'Negative':
                    explain += ' پروتئین در ادرار شما معمولی است '
                    explain += '\n\r'
                    continue
                elif value[i] >'Pos(+)' or 'Positive':
                    explain += ' پروتئین در ادرار شما طبیعی نیست ، لطفا به پزشک مراجعه کنید '
                    explain += '\n\r'
                    continue
            if item == 'Glucose':
                if value[i] == 'Negative':
                    explain += ' قند دفع شده در ادرار شما طبیعی است '
                    explain += '\n\r'
                    continue
                elif value[i] >'Pos(+)' or 'Positive':
                    explain += ' قند دفع شده در ادرار شما طبیعی نیست ، لطفا به پزشک مراجعه کنید'
                    explain += '\n\r'
                    continue
            if item == 'Keton' or 'Ketone':
                if value[i] == 'Negative':
                    explain += ' دفع کربوهیدرات در ادرار شما طبیعی است '
                    explain += '\n\r'
                    continue
                elif value[i] >'Pos(+)' or 'Positive':
                    explain += ' دفع کربوهیدرات در ادرار شما طبیعی نیست ، لطفا به پزشک مراجعه کنید '
                    explain += '\n\r'
                    continue
            if item == 'Blood':
                if value[i] == 'Negative':
                   explain += ' در ادرار شما خونی مشاهده نشده است و این وضعیت نرمال است '
                   explain += '\n\r'
                   continue
                elif value[i] >'Pos(+)' or 'Positive':
                    explain += ' در ادرار شما مقداری خون مشاهده شده است ، لطفا به پزشک مراجعه کنید '
                    explain += '\n\r'
                    continue
            if item == 'Bilirubin':
                if value[i] == 'Negative':
                    explain += ' مقدار بیلی روبین در ادرار شما طبیعی است و مشکل کلیوی از سمت ادرار شما یافت نشده است '
                    explain += '\n\r'
                    continue
                elif value[i] >'Pos(+)' or 'Positive':
                    explain += ' مقدار بیلی روبین در ادرار شما طبیعی نیست و شاید مشکل کلیوی از سمت ادرار وجود داشته باشد ، لطفا به پزشک مراجعه کنید '
                    explain += '\n\r'
                    continue
            if item == 'Urobilinogen':
                if value[i] == 'Negative':
                    explain += ' اوروبیلینوژن در ادرار شما طبیعی است و محلول های مضر دفع شده اند و به کلیه شما آسیبی نمیزنند '
                    explain += '\n\r'
                    continue
                elif value[i] >'Pos(+)' or 'Positive':
                    explain += ' اوروبیلینوژن در ادرار شما طبیعی نیست و محلول های مضر ممکن است برای شما مشکل کلیوی ایجاد کنند ، لطفا به پزشک مراجعه کنید '
                    explain += '\n\r'
                    continue
            if item == 'Nitrite':
                if value[i] == 'Negative':
                    explain += ' مقدار نیتریت ادرار شما طبیعی است و باکتری مضری در ادرار شما یافت نشد '
                    explain += '\n\r'
                    continue
                elif value[i] >'Pos(+)' or 'Positive':
                    explain += 'مقدار نیتریت ادرار شما طبیعی نیست و مقداری باکتری مضر در ادرار شما یافت شده است ، لطفا به پزشک مراجعه کنید'
                    explain += '\n\r'
                    continue
            if item =='Bacteria':
                if value[i] == '(Few)' or 'Few' or 'None':
                    explain += ' باکتری مضری در ادرار شما یافت نشد '
                    explain += '\n\r'
                    continue
                else:
                    explain += ' مقداری باکتری مضر در ادرار شما یافت شده است ، لطفا به پزشک مراجعه کنید '
                    explain += '\n\r'
                    continue
            if item =='Mucous' or 'Mucus':
                if value[i] == '(Few)' or 'Few' or 'None':
                    explain += ' التهاباتی در دستگاه ادراری شما یافت نشد '
                    explain += '\n\r'
                    continue
                else:
                    explain += ' التهاباتی در دستگاه ادراری شما یافت شده است لطفا به پزشک مراجعه کنید '
                    explain += '\n\r'
                    continue
        return explain