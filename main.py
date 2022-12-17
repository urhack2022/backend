from typing import Union

from fastapi import FastAPI, UploadFile, File
from schema import File as MyFile, QueryAnswer, AnswerNode
import aiofiles
from service import pdf_loader, make_request, annotate_pdf
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from docx2pdf import convert
from win32com import client as wc
from time import sleep


app = FastAPI()

origins = ["*"]

app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mappings = {'0':'Договоры поставки',
 '1': 'Договоры оказания услуг',
 '2': 'Договоры подряда',
 '3': 'Договоры аренды',
 '4': 'Договоры купли продажи',
 '': ''
}

w = wc.Dispatch('Word.Application')

@app.post('/file_upload')
async def file_upload(file: UploadFile = File()) -> QueryAnswer:
    filename = file.filename
    async with aiofiles.open('./static/'+filename, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    if filename.endswith('.doc'):
        print(filename)
        doc = w.Documents.Open('./static/'+filename)
        filename = filename.split('.')[0] + '.docx'
        doc.SaveAs(filename, 16)
        doc.Close()

    if filename.endswith(".docx"):
        filename = file.filename.split('.')[0] + '.pdf'
        convert('./static/'+file.filename, './static/'+filename)
    text = pdf_loader('./static/'+filename)
    request = make_request(text)
    print(request.json())
    annotations = [[], [], [], [], []]
    for par in request.json()['paragraphs']:
        annotations[int(par['text_type'])].append(par['original_text'])
    annotate_pdf('./static/'+filename, annotations)
    nodes = []
    for i in request.json()['paragraphs']:
        nodes.append(AnswerNode(text=i['original_text'], score=i['threshold'], predict_class=i['text_type']))
    return QueryAnswer(
        file='http://127.0.0.1:8000/static/'+filename, 
        predict_class=mappings[str(request.json()['text_type'])],
        nodes=nodes,
        sum_text=request.json()['text_summary']
    )


@app.post('/text-upload')
def text_upload() -> MyFile:
    return 'string'

@app.get('/queries')
def get_queries() -> list:
    return []
