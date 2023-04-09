from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession
from datetime import datetime,timedelta
import json
import time

timestr = time.strftime("%Y%m%d-%H%M%S")
file_name = timestr + ".json"
# 48 hours ago timestamp
time_begin = (datetime.utcnow() - timedelta(hours=48)).isoformat("T")+'Z'

credentials = Credentials.from_service_account_file(
    "creds.json",
    scopes=["https://www.googleapis.com/auth/admin.reports.audit.readonly"],
    subject="nancy.admin@hyenacapital.net",
)
authed_session = AuthorizedSession(credentials)

# collect events from last 48 hours
response = authed_session.get(
    "https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/TOKEN",
    params={"startTime": time_begin,"maxResults": 1000},
)

# store activity events
items = response.json()["items"]

# while the api request has token to second page
while "nextPageToken" in response.json():
    nextToken = response.json()["nextPageToken"]
    # make follow-on request getting the next page of the report
    response = authed_session.get(
        "https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/TOKEN",
        params={"startTime": time_begin,"maxResults": 1000, "pageToken": nextToken},
    )
    # append additional page's activity events
    items.extend(response.json()["items"])

# store events from last 48 hours in newline-delimited JSON file
with open(file_name,'w') as f:
    for i in items:
        json.dump(i,f)
        f.write('\n')