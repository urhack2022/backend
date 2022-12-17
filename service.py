import json
import requests as r
from tika import parser
import fitz
import re



def pdf_loader(path):    
    raw = parser.from_file(path)
    return raw['content']


color_map = [
    (1, 0, 1),
    (1, 1, 0),
    (1, 0, 0),
    (0, 1, 0),
    (0, 1, 1)
]


def annotate_pdf(filepath, highlighting):
    doc = fitz.open(filepath)
    texts = []
    for highlight in highlighting:
        text = list(map(lambda x: x.split('.'), highlight))
        text_res = []
        for i in text:
            text_res.extend(list(map(lambda x: x.strip(), i)))
        text = text_res
        text = map(
            lambda x: re.sub(
                r'\d+|  ',
                '',
                re.sub(r'\n|\r|\t', ' ', x)
            ),
            text
        )
        text = map(
            lambda x: ' '.join(
                filter(lambda xx: len(xx), x.split(' '))
            ),
            text
        )
        text = list(text)
        texts.append(text)
    for page in doc:
        text_instances = [[], [], [], [], []]
        for index, text in enumerate(texts):
            for t in text:
                if len(t.split(' ')) > 1:
                    try:
                        text_instances[index].extend(page.search_for(t))
                    except: pass

        for index, inst in enumerate(text_instances):
            for hl in inst:
                highlight = page.add_highlight_annot(hl)
                highlight.set_colors({"stroke": color_map[index]})
                highlight.update()
    doc.save(filepath, deflate=True, clean=True, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)


def make_request(string):
    ans = r.post("https://a02a-176-99-131-98.eu.ngrok.io/api", data=json.dumps({"text": string}), headers={'Content-Type': "application/json", 'Accept': "application/json"})
    try:
        print(ans.json())
    except: pass
    return ans