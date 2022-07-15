from interview.adapters import google_api, log
from interview.application import services


class Settings:
    google_api = google_api.Settings()


class Logger:
    log.configure()


class Resource:
    _client = google_api.Client(
        path_token=Settings.google_api.PATH_TOKEN,
        path_to_secrets=Settings.google_api.PATH_TO_SECRETS,
    )
    drive_resource = google_api.Drive(client=_client)
    form_resource = google_api.Forms(client=_client)
    sheet_resource = google_api.Sheet(
        client=_client, sheet_id=Settings.google_api.SHEET_ID
    )


class Application:
    form = services.Forms(
        drive_resource=Resource.drive_resource,
        form_resource=Resource.form_resource,
        sheet_resource=Resource.sheet_resource,
    )


Application.form.run(candidate_name='candidate_name')
