import datetime
import os.path

from oauth2client import file
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


from excel import get_questions, get_document


SCOPES = ["https://www.googleapis.com/auth/forms.body", 'https://www.googleapis.com/auth/drive', ]
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
EXCEL_DOCUMENT_ID = '1tsao56_qbI7vCwNyJRivKXpcSwtCpTTRD4zjjPeCRqU'
PATH_TO_TOKEN_FILE: str = 'token.json'
store = file.Storage(PATH_TO_TOKEN_FILE)
creds = None
if os.path.exists(PATH_TO_TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(PATH_TO_TOKEN_FILE, SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret_516941943654-lk9i695tnb4fjjo1ncfm30a0rclnclkf.apps.googleusercontent.com.json', SCOPES)
        creds = flow.run_local_server(port=0)
        if os.path.exists(PATH_TO_TOKEN_FILE):
            os.remove(PATH_TO_TOKEN_FILE)

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


form_service = build('forms', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)
sheets_service = build('sheets', 'v4', credentials=creds)
print('Введите Имя и фамилию кандидата')
name_candidate = input()
# Request body for creating a form
NEW_FORM = {
    "info": {
        "title": "Вопросы перед собеседованием",
        "document_title": f'Вопросы перед собеседованием для {name_candidate} время генерации: {datetime.datetime.now()}',
    }
}

# Request body to add a multiple-choice question
NEW_QUESTIONS = {
    "requests": []
}
NEW_INFO = {
    "requests": [{
        "updateFormInfo": {
             "info": {
                "description": "На вопросы необходимо ответить в течении 10 минут"

            },
            "updateMask": "description"

        }

    }]
}

questions = get_questions(filename=get_document(
    spreadsheet_id=EXCEL_DOCUMENT_ID, token=creds.token, sheets_service=sheets_service
))
location_index = 0
for question in questions:
    if question.body:
        image_section = {}
        if question.image:
            image_section = {
                'sourceUri': question.image
            }

        NEW_QUESTIONS['requests'].append({
            "createItem": {
                "item": {
                    "title": question.body,
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {
                                "paragraph": True
                            }
                        },
                        'image': image_section if image_section else None
                    },
                },
                "location": {
                    "index": location_index
                }
            }
        })
    location_index += 1

# Creates the initial form
result = form_service.forms().create(body=NEW_FORM).execute()
print(result['responderUri'])
# Adds the question to the form
form_service.forms().batchUpdate(formId=result["formId"], body=NEW_QUESTIONS).execute()
form_service.forms().batchUpdate(formId=result["formId"], body=NEW_INFO).execute()

print(f"https://docs.google.com/forms/d/{result['formId']}/edit#responses")
# Prints the result to show the question has been added
get_result = form_service.forms().get(formId=result["formId"]).execute()
print('delete form')
question = input()
if question:
    r = drive_service.files().delete(fileId=result['formId']).execute()


