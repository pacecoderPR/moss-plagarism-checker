import requests
import html
from bs4 import BeautifulSoup

languages = {
    'C (gcc 12.2.0)' : '.c',
    'Python (PyPy 3.10-v7.3.12)' : '.py',
    'Python (CPython 3.11.4)' : '.py',
    'Python (Mambaforge / CPython 3.10.10)' : '.py',
    'C++ 20 (gcc 12.2)' : '.cpp',
    'C++ 23 (gcc 12.2)' : '.cpp',
    'C++ 17 (gcc 12.2)' : '.cpp',
    'Java (OpenJDK 17)' : '.java',
    'JavaScript (Node.js 18.16.1)' : '.js',
    'JavaScript (Deno 1.35.1)' : '.js'
}
languages = {
    'c_cpp': '.c',
    'python': '.py',
    'javascript': '.js',
    'java': '.java'
}

def getSubmittedCode(submissionID,contest_code) :
    url = f"https://atcoder.jp/contests/{contest_code}/submissions/{submissionID}"

    response = requests.get(url)

    page = response.text
    soup = BeautifulSoup(page, "html.parser")
    pre_tag = soup.find('pre')
    source_code = html.unescape(pre_tag.text)
    language = pre_tag.attrs["data-ace-mode"]
    ext = languages[language]

    return [source_code,ext]

# submissionID = "45142566"

