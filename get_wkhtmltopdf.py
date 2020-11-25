"Utility to acquire a wkhtmltopdf executable appropriate for the current system and return its path"

import platform
import os
import distro
import requests

CONFIG = {"package-urls":
          {
           "ubuntu-focal": "https://github.com/zakird/wkhtmltopdf_binary_gem/blob/master/bin/wkhtmltopdf_ubuntu_20.04_amd64.gz?raw=true",
          }
         }


def get_wkhtmltopdf():
    "Acquire a wkhtmltopdf executable appropriate for the current system and return its path"

    plat = platform.system()

    if plat == "Windows":
        print("Fetching wkhtmltopdf not supported on Windows, ensure that wkhtmltopdf"
              "executable is present at "
              "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe.")
        return "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe."

    elif plat == "Linux":

        if os.path.exists("bin/wkhtmltopdf"):
            return "bin/wkhtmltopdf"

        distribution, _version, ver_name = distro.linux_distribution()

        if distribution == "Ubuntu" and ver_name == "focal":
            response = requests.get(CONFIG["package-urls"]["ubuntu-focal"])
            os.makedirs("./tmp/wkhtmltopdf")

            with open('./tmp/wkhtmltopdf/wkhtmltopdf.gz', 'wb') as output:
                output.write(response.content)

            os.system("gunzip ./tmp/wkhtmltopdf/wkhtmltopdf.gz")
            os.makedirs("./bin")
            os.rename("./tmp/wkhtmltopdf/wkhtmltopdf",
                      "./bin/wkhtmltopdf")
            os.system("chmod +x ./bin/wkhtmltopdf")
            return "./bin/wkhtmltopdf"

    raise OSError("Only Ubuntu Focal is supported for retrieving wkhtmltopdf"
                  "builds, place the downloaded executable at bin/wkhtmltopdf.")

if __name__ == "__main__":
    print(get_wkhtmltopdf())
