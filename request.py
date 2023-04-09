from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession
from datetime import datetime,timedelta
import json
import time
import operator

# Part 1
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

# Part 2
user_events = dict()
method_bytes = dict()
params = list()
# read 48 hours of data from Part 1, newline-delimited JSON file
with open(file_name) as f:
    for line in f:
        j_content = json.loads(line)
        # grab user information
        user = j_content["actor"]["profileId"]
        # grab api method and number of bytes to applications
        events = j_content["events"]
        api_method = ""
        api_bytes = 0
        for e in events:
            for sub_e in e["parameters"]:
                # method name for an event instance
                if sub_e["name"] == "method_name":
                    api_method = sub_e["value"]
                # number of bytes for an event instance
                elif sub_e["name"] == "num_response_bytes":
                    api_bytes = int(sub_e["intValue"])
        # update number of event associated with user
        user_events[user] = user_events.get(user,0) + 1
        # update number of bytes an api method uses. sum
        method_bytes[api_method] = method_bytes.get(api_method,0) + api_bytes

max_user = max(user_events.items(),key=operator.itemgetter(1))[0]
max_api_method = max(method_bytes.items(),key=operator.itemgetter(1))[0]
sorted_user_events = dict(sorted(user_events.items(), key=operator.itemgetter(1),reverse=True))
sorted_method_bytes = dict(sorted(method_bytes.items(), key=operator.itemgetter(1),reverse=True))
print(f'User with most number of events (ID): {max_user}')
print(f'API method with most number of bytes: {max_api_method}')
print('----------------------------------------------------------')
print('Complete list of events per user:')
print(sorted_user_events)
print('Complete list of number of bytes per API method:')
print(sorted_method_bytes)