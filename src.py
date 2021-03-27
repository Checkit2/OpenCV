#region libraries
import cv2
import pytesseract
from pytesseract import Output
import pandas as pd
#endregion

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process(img_path):
    
    img = cv2.imread(img_path)
    # img = cv2.resize(img,(600,210))
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
        
    return text

def check_words(text):
    text = (text.split())
    keyword_list = ['Specific Gravity','Semi Turbid','Epithelial cells/Lpf','Amorphus urate Few','RBCih  pf','RBC/h p f','Ep Celis /h.p.f','Semi clear','Yeltow','Blood (Hemoglobin)','W.B.C    /h.p.f','R.B.C    —/h.p.f','R.B.C    /h.p.f','Ep.Cells /h.p.f','Bacteria /h.p.f','Crystals /h.p.f','Casts    /h.p.f','Mucus    /h.p.f','Spore of fungi','*Positive 2+','RBCihPf','WECih.pt',"WBCthpr","RBCApfe","Yeutow","Giucose"]
    matching_list = ['SpecificGravity','SemiTurbid','EpithelialCells/Lpf','AmorphusUrateFew','RBCihPf','RBC/hpf','EpCelis/h.p.f','SemiClear','yellow','Blood(Hemoglobin)','W.B.C/h.p.f','R.B.C/h.p.f','R.B.C/h.p.f','Ep.Cells/h.p.f','Bacteria/h.p.f','Crystals/h.p.f','Casts/h.p.f','Mucus/h.p.f','SporeOfFungi','*Positive2+','RBC/h.p.f','WBC/h.p.f',"WBC/hpf","RBC/hpf","Yellow","Glucose"]
    for i,item in enumerate(keyword_list):
        if item in text:
            text = text.replace(item , matching_list[i])

    return text
    
def bad_words(text):
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
    
    return text

def find_similar(search_for, dataset):
    res = []
    from rapidfuzz import fuzz
    import operator
    for data in dataset:
        res.append(fuzz.ratio(search_for, data))
    i, v = max(enumerate(res), key=operator.itemgetter(1))
    yield dataset[i]
    yield v

# print(text)
# exit(0)
def datasetes(text):
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

    # def count(string, element):
    #     count=0
    #     for i in range(len(string)):
    #         if string[(i*-1)] == element:
    #             count+=1
    #     return count

    key_list = []
    value_list = []
    allowed_accurancy = 75
    for i, t in enumerate(text):    
        if i%2 == 0:
            word, accuracy = find_similar(t, dataset)
            if accuracy > allowed_accurancy:
                text[i] = word
                key_list.append(t)
        else:
            value_list.append(t)
    return key_list
    return value_list

# print(key_list)
# print(value_list)
# exit(0)

def keys(text):  
    ql = []
    c = 0
    for item in key_list:
        q = {
            "key":key_list[c],
            "value":value_list[c]
        }
        c += 1
        ql.append(q)
    

    print(len(key_list))
    print(len(value_list))    

def send(text):
    import json
    requestJson = json.dumps(ql)

    # print(requestJson)



text = process('test-crop.jpg')
text = check_words(text)
text = bad_words(text)
text = find_similar(text)
text = datasetes(text)
text = keys(text)
send(text)