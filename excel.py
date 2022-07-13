from typing import Optional, List, Dict

from openpyxl import load_workbook
import random
from dataclasses import dataclass

import io
import re

from urllib3.util import parse_url

import requests



def get_document(sheets_service, token: str, spreadsheet_id: str) -> io.BytesIO:
    result = sheets_service.spreadsheets().get(spreadsheetId = spreadsheet_id, includeGridData=True).execute()
    urlParts = parse_url(result['spreadsheetUrl'])
    path = re.sub("\/edit$", '/export', urlParts.path)
    url = urlParts._replace(path=path)

    headers = {
      'Authorization': 'Bearer ' + token,
    }
    response = requests.get(url, headers = headers)
    return io.BytesIO(response.content)


@dataclass
class Question:
    body: str
    image: Optional[str]


def get_questions(
        filename: str = 'questions.xlsx', max_question_in_theme: int = 2, max_questions: int = 10,
) -> List[Question]:
    wb = load_workbook(filename)
    questions = []
    for worksheet in wb.worksheets:
        theme_questions = [
            Question(body=line[0], image=line[1])
            for line in worksheet.values
        ][1:]
        if len(theme_questions) > 0:
            for i in range(0, max_question_in_theme, 1):
                choice = random.choice(theme_questions)
                if choice.body:
                    questions.append(choice)
                theme_questions.remove(choice)
                if len(theme_questions) == 0:
                    break
    result = []
    for i in range(0, max_questions, 1):
        if len(questions) > 0:
            choice = random.choice(questions)
            result.append(choice)
            questions.remove(choice)

    return result
