from pydantic import BaseModel
from typing import List

class File(BaseModel):
    url: str
    name: str


class AnswerNode(BaseModel):
    text: str
    predict_class: str
    score: float

class QueryAnswer(BaseModel):
    file: str
    predict_class: str
    nodes: List[AnswerNode]
    sum_text: str