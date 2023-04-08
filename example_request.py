from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession

credentials = Credentials.from_service_account_file(
    "creds.json",
    scopes=["https://www.googleapis.com/auth/admin.reports.audit.readonly"],
    subject="nancy.admin@hyenacapital.net",
)

authed_session = AuthorizedSession(credentials)

response = authed_session.get(
    "https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/TOKEN",
    params={"maxResults": 1},
)

print(response.json())