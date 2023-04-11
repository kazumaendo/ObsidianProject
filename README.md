# Take Home problem

## Assumptions
1. User can uniquely be identified by their profileId
2. Subsequent runs of the script can append activity log to previous collection or start clean
3. Get request to Google's Admin Reports API will return consistent data when provided with startTime and endTime parameters
4. api method which returns the most number of bytes to applications can be calculated by summing all of the bytes used by an api method
5. Result of the analysis can be printed in the command line


## Solution Formulation
1. Collect past 48 hours of activity log and store it in a newline-delimited JSON file
2. Analyze token activity using dictionary counter
3. Get the subsequent script run to resume collection from where last collection left off
4. Minimize miss in between runs by logging file name and most recent timestamp of the latest run of the script

## How to Run
Have Docker installed and running.

Run the following in command line:
```
docker build -t obsidian-kazuma .
```
```
docker run -t -i -v $(pwd):/code obsidian-kazuma
```

For subsequent runs of the script, you will be prompted 
```
Do you want to combine activity log with previous run? y/n:
```
'y': activity log of the current run will be combined with the last collection. Thus, analysis will contain information from last run

'n': opposite of 'y'
