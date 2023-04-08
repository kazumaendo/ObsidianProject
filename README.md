# Take Home problem

## Contents

Besides this README, we've included:

1. a credentials file `creds.json`.
2. starter code `example_request.py` that authenticates with this credential file and makes an example request to the activity api for TOKEN events.
3. the `requirements.txt` file describing the Python dependencies needed for this starter code to run.

Feel free to use any libraries/sdks as desired.
Clarity and Correctness of code are what we are looking for.

## Problems

### 1. Retrieving TOKEN activity data using Google's Admin Reports API

The desired result is a Python script that retrieves token activity events from the Google Workspace API.

- The first time this script is run, we should collect events from the last 48 hours.
  - the results should be stored in a newline-delimited JSON file.
- Subsequent runs of the script should resume collection from where the last collection left off.
  - each run should store its events in another newline-delimited JSON file.  
  - we would like to ensure as best as we can that we do not miss any events between runs.
  - state can be stored on the local filesystem.

### 2. Analyze token activity

Once 48 hours of data from problem (1.) has been collected:

- Identify the user with the most number of events.
- Which api method (see `method_name` parameter) has returned the most number of bytes to applications?
  
## API Reference

- [https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-tokens](https://developers.google.com/admin-sdk/reports/v1/guides/manage-audit-tokens)  
- [https://developers.google.com/admin-sdk/reports/reference/rest/v1/activities/list](https://developers.google.com/admin-sdk/reports/reference/rest/v1/activities/list)  
