"Module which uses wkhtmltopdf to generate PDF bytestrings from HTML strings"

import subprocess
from bs4 import BeautifulSoup

def fix_sources(html_text):
    soup = BeautifulSoup(html_text)

    demo_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACoAAAAqCAYAAADFw8lbAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwgAADsIBFShKgAAAABh0RVh0U29mdHdhcmUAcGFpbnQubmV0IDQuMS4xYyqcSwAAAfhJREFUWEfVjout3DAMBK+ntJOaXssO+WAGq/VQn0sCXAYY2FqKFF/Xdf0XYviJYrjrzx9f167eeyqGK2mRE33ejhh20qN/os+fiaFLj6jKrN7U8E0XQ5WGq8SsrjW5g2+rGJY01E3qW2hNqZwMcIcSw5SGkUl9Cz8r2usGuEuKIQ3pTOqbaO5UbWaAO2FIAzqT+ib6r2jPyuCx0yOgxh076O7K4LHXI6DGHWfQ/ZXBsNdwoIYTV1BPZzDsNhyoIS2o5hJ0Ly2olgbPReliqVBdLaimKlRPg/1Fi/r3uuaO1tzKC6/ftbNFd876TahWrs6S7y1a7GT67TKv6TnRTGrzRRP9/5fQm5LtL6qZ0uXOql/rkJ0vWlKtg+55VlItWC+aeF41ygi651nlCeTzRe9L36zyFV3fKr9r60VThzKl61O6uW7we7/jRWf8zd67/7loChe38d7yBOg9X9TPive5HV6znmG34aAXpeFxVrSm9S4vvKbnOxt2Gw6pN5BFlxdd3XMyGPYaDik1uQllBN3zzA0eez2ClJpnKrNsxwB3wjClIaRyUusMcB8MSxqkOqd1N8A9UgxVGqg6q7wzwPdLDF0arK6gHjXAd1UMSXrAdeiOGuBbJIYz6cF39LkrMdyRHl/pM07E8B1psdTvvSuGnyiGn+f1+gVIfUjDmZb3NwAAAABJRU5ErkJggg=="

    images = soup.find_all("img")
    for image in images:
        image["src"] = demo_uri
        
    return str(soup)

def html2pdf(html_text):
    "Generate a bytestring of the string html_text in .pdf format"

    # https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
    process = subprocess.Popen(['C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe',
                                '--enable-local-file-access',
                                "--log-level",
                                "error",
                                '-',
                                '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    out, err = process.communicate(input=fix_sources(html_text).encode("utf-8"))

    if process.returncode != 0:
        raise IOError("Error generating PDF, wkhtmltopdf raised:\n"+err.decode("utf-8"))

    return out
