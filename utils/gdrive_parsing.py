"Provide a class to fetch file structure and content from Google Drive"

from __future__ import print_function
import urllib.parse
import io

from bs4 import BeautifulSoup

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from .resources import ResourceFolder, HTMLResource

def id_from_name(name):
    "Generate a url-safe ID from a pretty name"
    return urllib.parse.quote_plus(name.replace(" ", "-")).lower()

class DriveScraper():
    "Class to fetch folder structure and Docs content from a Drive folder"
    def __init__(self, api_key):
        self.drive_service = build("drive", "v3", developerKey = api_key)

    def fetch_simplified_doc_html(self, doc_id):
        "Get usable HTML for a Doc by its ID"
        request = self.drive_service.files().export(fileId=doc_id, mimeType="text/html")

        file_object = io.BytesIO()
        downloader = MediaIoBaseDownload(file_object, request)

        done = False
        while done is False:
            _status, done = downloader.next_chunk()

        file_object.seek(0)
        html = file_object.read().decode("utf-8")

        soup = BeautifulSoup(html, "html.parser")

        body = soup.body

        for element in body.findChildren():
            if element.get("style"):
                del element["style"]

            if element.get("id"):
                del element["id"]

            # Spans appear to be completely useless in Docs HTML output
            if element.name == "span":
                element.unwrap()

            if element.name == "h2":
                element["id"] = element.text.replace(" ", "-").lower()

            if element.name == "img":
                container = soup.new_tag('div', **{"class":"inline-image"})
                element.wrap(container)

            if element.name == "table":
                cells = element.find_all("td")
                if cells[0].text == "{{microbitembed}}":
                    embed_id = cells[1].text

                    blocks_container = soup.new_tag("div")
                    blocks_container["class"] = "code"

                    if len(cells) >= 3:
                        embed_content = cells[2]
                        blocks_container["class"] = "code"
                        blocks_explanation = soup.new_tag("div")
                        blocks_explanation["class"] = "code-explanation"
                        blocks_explanation.append(embed_content)
                        blocks_container.append(blocks_explanation)

                    else:
                        blocks_container["class"] = "code-notext code"

                    blocks_jinja_embed = '''{% with code_url="''' + embed_id + '''" %}{% include 'code.html' %}{% endwith %}'''

                    blocks_container.append(BeautifulSoup(blocks_jinja_embed, "html.parser"))

                    element.replace_with(blocks_container)
                elif cells[0].text == "{{codeblock}}":
                    code_content = cells[1]

                    code_block = soup.new_tag("div")
                    code_block["class"] = "inline-code"
                    code_block.append(code_content)

                    print(code_block)

                    element.replace_with(code_block)

        body.unwrap()

        return str(soup)

    def fetch_file_query_results(self, query):
        "Get de-paginated results for a file query (vulnerable to injection!)"
        page_token = None
        while True:
            response = self.drive_service.files().list(q=query,
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name, mimeType)',
                                                pageToken=page_token).execute()

            for file in response.get('files', []):
                yield file

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    def enumerate_gdrive_folder(self, gdrive_id, folder_name):
        "Enumerate a google drive folder, returning its structure as a ResourceFolder"
        contents = []

        files = list(self.fetch_file_query_results(f"'{gdrive_id}' in parents"))

        for file in files:
            if file.get("mimeType") == 'application/vnd.google-apps.folder':
                contents.append(self.enumerate_gdrive_folder(file["id"], file.get("name")))

            elif file.get("mimeType") == 'application/vnd.google-apps.document':
                contents.append(HTMLResource(self.fetch_simplified_doc_html(file.get("id")), 
                                            file.get("name"),
                                            id_from_name(file["name"])))
        return ResourceFolder(contents,
                              folder_name,
                              id_from_name(folder_name))
