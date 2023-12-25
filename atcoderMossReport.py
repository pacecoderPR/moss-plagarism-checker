import requests
import urllib.parse
import json
import fetch_code_from_subID as fetchCode
import os
import subprocess
import sheetsFunctions
from configparser import ConfigParser
import sys
import shelve

contest_code = sys.argv[1]

shelfFile = shelve.open('completedContests')
if contest_code not in shelfFile.keys():
    shelfFile[contest_code] = []

# Read the submissions directory path from config file
configObject = ConfigParser()
configObject.read("config.ini")
paths = configObject["PATHS"]
sheets = configObject["GOOGLE SHEETS"]

#Create a directory inside submissions folder
contestDirectory = os.path.join(paths["submissions_directory"], "submissions", contest_code)
if os.path.isdir(contestDirectory) == False:
    os.makedirs(contestDirectory)

loginUrl = "https://atcoder.jp/login"
languages = {
    '.py': 'python',
    '.c': 'c',
    '.cpp': 'cc',
    '.js': 'javascript',
    '.java': 'java'
}

def fetch_cookie(response):
    set_cookie = response.headers['Set-Cookie']

    cookie = set_cookie.split(',')
    cookie[0] = cookie[0].split(";")[0]
    cookie[1] = cookie[1].split(";")[0]
    cookie = cookie[0] + ';' + cookie[1]

    return cookie


response = requests.get(loginUrl)

csrf_encoded = response.headers['Set-Cookie'].split('csrf_token')[1].split('%00')[0]
csrf = urllib.parse.unquote(csrf_encoded).split(':')[1]

data = {
    "username": "navgurukul",
    "password": "navgurukul123",
    "csrf_token": csrf
}

dataHeaders = {
    'Cookie': fetch_cookie(response)
}

response = requests.post(loginUrl, data=data, headers=dataHeaders, allow_redirects=False)
authenticatedCookie = fetch_cookie(response)

dataHeaders = {
    'Cookie': authenticatedCookie
}

standingsUrl = f"https://atcoder.jp/contests/{contest_code}/standings/json"
response = requests.get(standingsUrl, headers=dataHeaders)

ranking = json.loads(response.text)

submittedLanguagesExt = set()

# Load usernames from student and team google sheet
desired_users = []
desired_users += sheetsFunctions.fetch_usernames(sheets["student_username_sheet_id"], sheets["student_username_sheet_range"])
desired_users += sheetsFunctions.fetch_usernames(sheets["team_username_sheet_id"], sheets["team_username_sheet_range"])


for value in ranking['StandingsData']:
    username = value['UserName']
    if username in desired_users:

        if username in shelfFile[contest_code]:
            continue
        # Rest of the code inside this block
        result = value['TaskResults']
        for problem_code in result:

            submissionID = result[problem_code]['SubmissionID']
            if submissionID != 0 :
                code, ext = fetchCode.getSubmittedCode(submissionID,contest_code)

                if ext == "":
                    print(submissionID)

                #create directory inside contest code directory
                directoryName = os.path.join(contestDirectory, problem_code, languages[ext])
                if os.path.isdir(directoryName) == False:
                    os.makedirs(directoryName)
                submittedLanguagesExt.add(ext)
                filePath = os.path.join(directoryName, f"{username}_{submissionID}{ext}")

                #check if file already exists
                if os.path.isfile(filePath) == False:
                    with open(str(filePath),'w') as myFile:
                        myFile.write(code)

        shelfFile[contest_code] += [username]

shelfFile.close()
print(f"Submitted languages in contest: {submittedLanguagesExt}")

# List that stores the links
data = [contest_code, "", "", "", "", "", "", "", "", ""]

for folderPath, subfolders, filenames in os.walk(contestDirectory):
    # Run MOSS only if there are 2 or more files to compare
    if len(filenames) > 1:
        p, language = os.path.split(folderPath)
        p, task = os.path.split(p)
        task = task[-1].upper()

        command_result = subprocess.check_output(f"perl {paths['moss_script_directory']}/moss.pl -l {language} {folderPath}/*", shell = True)
        command_result = command_result.decode('ascii').split("\n")
        report_link = command_result[-2]
        print(f"link generated for problem {task} in `{language}` language: {report_link}")
        data[ord(task) - 64] += f"{language} - {report_link}\n\n"

# Write links to google sheet
sheetsFunctions.write_links(sheets["plagiarism_sheet_id"], data)
