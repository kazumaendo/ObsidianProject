from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession
from datetime import datetime,timedelta
from os.path import exists
import os
import json
import time
import operator

# returns the events and the most recent timestamp of the events
def api_request(authed_session,start_time,end_time):
    # collect events
    response = authed_session.get(
        "https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/TOKEN",
        params={"startTime": start_time,"endTime": end_time,"maxResults": 1000},
    )

    if "items" not in response.json():
        print("Please wait until there are more logs")
    # store activity events
    events = response.json()["items"]
    top_time = events[0]["id"]["time"]
    dt = datetime.strptime(top_time,'%Y-%m-%dT%H:%M:%S.%fZ')
    top_time = (dt + timedelta(milliseconds=1)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    # while the api request has token to second page
    while "nextPageToken" in response.json():
        nextToken = response.json()["nextPageToken"]
        # make follow-on request getting the next page of the report
        response = authed_session.get(
            "https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/TOKEN",
            params={"startTime": start_time,"endTime": end_time,"maxResults": 1000, "pageToken": nextToken},
        )
        # append additional page's activity events
        events.extend(response.json()["items"])
    return events,top_time


def load_data(file_name,cur_time):
    credentials = Credentials.from_service_account_file(
        "creds.json",
        scopes=["https://www.googleapis.com/auth/admin.reports.audit.readonly"],
        subject="nancy.admin@hyenacapital.net",
    )
    authed_session = AuthorizedSession(credentials)

    # if subsequent run of the script
    if exists(os.path.join(os.getcwd(),'previous_time.txt')):
        with open('previous_time.txt') as f:
            prev_runtime = f.readline()

        items,top_time = api_request(authed_session,prev_runtime,cur_time)
                
        with open(file_name,'w') as f:
            for i in items:
                json.dump(i,f)
                f.write('\n')    
        
        # collect whether to combine events with previous run
        while True:
            combine = input('Do you want to combine activity log with previous run? y/n: ')
            if combine.lower() == 'y' or combine.lower() == 'n':
                break
            else:
                print('Please type y/n')

        # if combine events is True, extend the events
        if combine == 'y':
            result = list()
            prev_file = ''
            # get previous events file
            with open('previous_activity_file.txt') as in_f:
                prev_file = in_f.readline()
            for f1 in [file_name,prev_file]:
                data = [json.loads(line) for line in open(f1, 'r')]
                result.extend(data)
                
            with open(file_name,'w') as f:
                for r in result:
                    json.dump(r,f)
                    f.write('\n') 
        
        # log the time subsequent script should pick up from
        with open('previous_time.txt','w') as f:
            f.write(top_time)
        # log the activity file subsequent script should pick up from
        with open('previous_activity_file.txt','w') as f:
            f.write(file_name)

    # if first time script is run
    else:
        # 48 hours ago timestamp
        dt = datetime.strptime(cur_time,'%Y-%m-%dT%H:%M:%S.%fZ')
        time_begin = (dt - timedelta(hours=48)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        items,top_time = api_request(authed_session,time_begin,cur_time)

        # store events from last 48 hours in newline-delimited JSON file
        with open(file_name,'w') as f:
            for i in items:
                json.dump(i,f)
                f.write('\n')
        
        # log the time subsequent script should pick up from
        with open('previous_time.txt','w') as f:
            f.write(top_time)
        # log the activity file subsequent script should pick up from
        with open('previous_activity_file.txt','w') as f:
            f.write(file_name)


def analyze(file_name):
    # Part 2
    user_events = dict()
    method_bytes = dict()
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

def main():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    file_name = timestr + ".json"
    cur_time = datetime.utcnow().isoformat("T")+'Z'
    load_data(file_name,cur_time)
    analyze(file_name)

if __name__ == "__main__":
    main()