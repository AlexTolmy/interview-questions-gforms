import os
import os.path

from classic.components import component
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from oauth2client import file

from .constaints import GOOGLE_RESOURCES_MAPPING, SCOPES, GoogleResources


@component
class Client:
    path_token: str
    path_to_secrets: str

    def __attrs_post_init__(self):
        self.store = file.Storage(self.path_token)
        self._creds = None

    def _auth(self):
        if os.path.exists(self.path_token):
            self._creds = Credentials.from_authorized_user_file(
                self.path_token, SCOPES
            )

        if not self._creds or not self._creds.valid:
            if self._creds and self._creds.expired and self._creds.refresh_token:
                self._creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.path_to_secrets, SCOPES
                )
                self._creds = flow.run_local_server(port=0)
                if os.path.exists(self.path_token):
                    os.remove(self.path_token)

            with open(self.path_token, 'w') as token:
                token.write(self._creds.to_json())

    @property
    def _get_credentials(self):
        self._auth()
        return self._creds

    @property
    def get_token(self):
        return self._get_credentials.token

    def create_resource(self, resource_name: GoogleResources) -> Resource:
        args = GOOGLE_RESOURCES_MAPPING[resource_name]
        return build(*args, credentials=self._get_credentials)
