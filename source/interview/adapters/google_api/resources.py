import io
import logging
import re
from typing import List, Optional

import requests
from classic.components import component
from googleapiclient.errors import HttpError
from interview.adapters.google_api import Client
from interview.adapters.google_api.constaints import GoogleResources
from interview.application import interfaces
from interview.application.dto import FromInfo, Question, Theme
from openpyxl import load_workbook
from urllib3.util import parse_url


@component
class Forms(interfaces.StorageForm):
    client: Client

    def __attrs_post_init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._resource = self.client.create_resource(GoogleResources.form)

    def create(self, title: str, form_title: str) -> FromInfo:
        result = self._resource.forms().create(
            body=self._make_body_title(title=title, form_title=form_title)
        ).execute()
        self._create_view_url(result['formId'])
        _id = result['formId']
        return FromInfo(
            view_form_url=result['responderUri'],
            id=_id,
            response_url=self._create_view_url(_id)
        )

    def create_questions(self, _id: str, questions: List[Question]):
        self._resource.forms().batchUpdate(
            formId=_id, body=self._make_body_questions(questions)
        ).execute()

    def create_description(self, _id: str, description: str):
        self._resource.forms().batchUpdate(
            formId=_id, body=self._make_body_description(description)
        ).execute()

    @staticmethod
    def _create_view_url(_id: str):
        return f'https://docs.google.com/forms/d/{_id}/edit#responses'

    @staticmethod
    def _make_body_title(title: str, form_title: str):
        body = {'info': {'title': title, 'document_title': form_title}}
        return body

    @staticmethod
    def _make_body_questions(questions: List[Question]):
        location_index = 0
        body = {'requests': []}
        for question in questions:
            image_section = {}
            if question.image_url:
                image_section = {'sourceUri': question.image_url}

            body['requests'].append(
                {
                    'createItem': {
                        'item': {
                            'title': question.text,
                            'questionItem': {
                                'question': {
                                    'required': True,
                                    'textQuestion': {
                                        'paragraph': True
                                    }
                                },
                                'image': image_section
                                if image_section else None
                            },
                        },
                        'location': {
                            'index': location_index
                        }
                    }
                }
            )
            location_index += 1

        return body

    @staticmethod
    def _make_body_description(description: str):
        body = {
            'requests': [
                {
                    'updateFormInfo': {
                        'info': {
                            'description': description
                        },
                        'updateMask': 'description'
                    }
                }
            ]
        }
        return body


@component
class Drive(interfaces.StorageDrive):
    client: Client

    def __attrs_post_init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._resource = self.client.create_resource(GoogleResources.drive)

    def delete(self, _id: str):
        try:
            self._resource.files().delete(fileId=_id).execute()
        except HttpError as e:
            if not e.status_code == 404:
                raise e

            self.logger.error(e.error_details)


@component
class Sheet(interfaces.StorageSheet):
    client: Client
    sheet_id: str

    def __attrs_post_init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._resource = self.client.create_resource(GoogleResources.sheets)

    def get(self) -> List[Theme]:
        result = self._resource.spreadsheets().get(
            spreadsheetId=self.sheet_id, includeGridData=True
        ).execute()

        url = self._make_url(_url=result['spreadsheetUrl'])
        document = self._get_data(url)

        return self._parse(document)

    @staticmethod
    def _make_url(_url: str) -> str:
        url_parts = parse_url(_url)
        path = re.sub('\/edit$', '/export', url_parts.path)

        return url_parts._replace(path=path)

    def _get_data(self, url: str) -> io.BytesIO:
        headers = {
            'Authorization': 'Bearer ' + self.client.get_token,
        }
        response = requests.get(url, headers=headers)

        return io.BytesIO(response.content)

    @staticmethod
    def _parse(document: io.BytesIO) -> List[Theme]:
        wb = load_workbook(document)

        themes = []
        for worksheet in wb.worksheets:
            questions = [
                Question(text=line[0], image_url=line[1])
                for line in worksheet.values
                if line[0]
            ][1:]
            themes.append(
                Theme(**{
                    'title': worksheet.title,
                    'questions': questions
                })
            )
        return themes
