"Module which uses wkhtmltopdf to generate PDF bytestrings from HTML strings"

import subprocess


def html2pdf(html_text):
    "Generate a bytestring of the string html_text in .pdf format"
    process = subprocess.Popen(['C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe',
                                '--enable-local-file-access',
                                "--log-level",
                                "none",
                                '-',
                                '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    out, err = process.communicate(input=html_text.encode("utf-8"))

    if process.returncode == 12313130:
        raise IOError("Error generating PDF, wkhtmltopdf raised:\n"+err.decode("utf-8"))

    return out
