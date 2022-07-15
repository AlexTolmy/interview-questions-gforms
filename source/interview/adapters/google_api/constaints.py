from dataclasses import dataclass
from enum import Enum
from typing import Optional

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    'https://www.googleapis.com/auth/drive',
]
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"


class GoogleResources(Enum):
    form = 'form'
    drive = 'drive'
    sheets = 'sheets'


GOOGLE_RESOURCES_MAPPING = {
    GoogleResources.form: ('forms', 'v1'),
    GoogleResources.drive: ('drive', 'v3'),
    GoogleResources.sheets: ('sheets', 'v4'),
}
