"Module which uses wkhtmltopdf to generate PDF bytestrings from HTML strings"

import subprocess
from bs4 import BeautifulSoup
import base64
import re
import requests
import get_wkhtmltopdf

wkhtmltopdf_executable = get_wkhtmltopdf.get_wkhtmltopdf()

def is_url_external(url):
    if re.search("^(?:[a-z]+:)?//", url):
        return True
    else:
        return False

def fix_sources(html_text, app):
    with app.test_client() as client:
        soup = BeautifulSoup(html_text)

        for image in soup.find_all("img"):
            response = client.get(image["src"])
            data = response.data
            mimetype = response.mimetype

            encoded_data = base64.b64encode(data).decode("utf-8")

            image["src"] = "data:{mimetype};base64,{encoded_data}".format(mimetype=mimetype, encoded_data=encoded_data)

           

        for link in soup.find_all("link"):
            if "stylesheet" in link["rel"]:
                if is_url_external(link["href"]):
                    response = requests.get(link["href"])
                    data = response.text
                else:
                    response = client.get(link["href"])
                    data = response.data.decode("utf-8")

                link["href"] = "data:text/css,{data}".format(data=data)
            
    return str(soup)

def html2pdf(html_text, app):
    "Generate a bytestring of the string html_text in .pdf format"

    # https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
    process = subprocess.Popen([wkhtmltopdf_executable,
                                '--enable-local-file-access',
                                "--log-level",
                                "info",
                                "--header-left",
                                "Perse Coding Outreach",
                                "--header-spacing",
                                "1",
                                '-',
                                '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    out, err = process.communicate(input=fix_sources(html_text, app).encode("utf-8"))

    if process.returncode != 0:
        raise IOError("Error generating PDF, wkhtmltopdf raised:\n"+err.decode("utf-8"))

    return out
