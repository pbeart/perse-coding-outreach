"""Flask app to serve application so it can be frozen to static files.
Not particularly performant because it is never used in production"""

import os.path
import os

from bs4 import BeautifulSoup
from flask import Flask, render_template, render_template_string, abort
app = Flask(__name__)

from utils import gdrive_parsing, yaml_parsing, resources


def load_all_resources(content_yaml_path=None, gdrive_folder_id=None):
    "Load all resources from YAML and GDrive sources"
    if gdrive_folder_id:
        gdrive_scraper = gdrive_parsing.DriveScraper(os.environ["GDRIVE_API_KEY"])
        gdrive_resources = gdrive_scraper.enumerate_gdrive_folder(gdrive_folder_id, "resources")
    else:
        gdrive_resources = None

    if content_yaml_path:
        yaml_resources = yaml_parsing.fetch_yaml_resources(content_yaml_path)
    else:
        yaml_resources = None

    merged_resources = resources.ResourceFolder([], "Resources", "resources")

    merged_resources = merged_resources.merged_with(yaml_resources)
    merged_resources = merged_resources.merged_with(gdrive_resources)

    return merged_resources

all_resources = load_all_resources("content-index.yaml", os.environ.get("GDRIVE_FOLDER_ID"))

def contents_list(html_text):
    "Generate a contents list from the provided HTML"

    soup = BeautifulSoup(html_text)
    headers = soup.find_all("h2")
    contents = []
    for header in headers:
        if header.get("id"):
            contents.append([header.text, header["id"]])

    return contents

@app.context_processor
def resource_type():
    "Add Jinja-available function to get the type of a resource object"
    def _resource_type(resource):
        if isinstance(resource, resources.ResourceFolder):
            return "ResourceFolder"
        elif isinstance(resource, resources.FileResource):
            return "FileResource"
        elif isinstance(resource, resources.HTMLResource):
            return "HTMLResource"
        elif isinstance(resource, resources.LinkResource):
            return "LinkResource"
        return "None"
    return {"resource_type": _resource_type}

def get_path_urls_aliases_at_path(path):
    """Return a list of tuples containing url and display name for each
    stage in a path, like [('/folder/item', 'Item'), ...],"""
    output = []

    path_elements = path.split("/")


    for index in range(len(path_elements)):
        tree = all_resources.get_at_path("/".join(path_elements[:index]))
        output.append(["/resources" + "/".join(path_elements[:index]), tree.name])

    return output

def generate_path_indicator(path):
    "Generate a list used to generate a path indicator from the given path"
    path_url_pairs = get_path_urls_aliases_at_path(path)
    return [["/", "Home"], *path_url_pairs]


def render_directory_listing(path):
    "Render a directory listing page for the given path."

    tree = all_resources.get_at_path(path)

    path_elements = [element for element in path.split("/") if element != ""]

    if len(path_elements) == 0:
        base_path = "/resources"
    else:
        base_path = "/resources/" + "/".join(path_elements)

    return render_template("resources_subsection.html",
                           tree=tree,
                           title=tree.name,
                           base_url_path = base_path,
                           resource_path=generate_path_indicator(path))

@app.route('/')
def route_home():
    "Homepage"
    return render_template("index.html")

@app.route('/resources/<path:resource_name>/')
def route_resource(resource_name):
    "Fetch a resource"

    try:
        resource = all_resources.get_at_path(resource_name)
    except KeyError:
        abort(404)

    if isinstance(resource, resources.ResourceFolder):
        return render_directory_listing(resource_name)

    elif isinstance(resource, resources.FileResource):
        try:
            with open(resource.file_path + ".html") as resource_file:
                resource_content = render_template_string(resource_file.read())

            return render_template("resource.html",
                                resource_html = resource_content,
                                resource_path = generate_path_indicator(resource_name),
                                resource_name = resource.name,
                                contents_list = contents_list(resource_content))
        except FileNotFoundError:
            abort(404)

    elif isinstance(resource, resources.HTMLResource):
        return render_template("resource.html",
                               resource_html = resource.html,
                               resource_path = generate_path_indicator(resource_name),
                               resource_name = resource.name,
                               contents_list = contents_list(resource.html))
    else:
        abort(404)


@app.route('/resources/')
def route_resources():
    "Root resources listing"
    return render_directory_listing("")


@app.errorhandler(404)
def route_not_found(_e):
    "Handle 404"
    return render_template('404.html'), 404



# Disable caching for development. Has no impact on
# production as this is lost when rendering to static
@app.after_request
def add_header(request):
    "Add post-request headers"
    request.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    request.headers["Pragma"] = "no-cache"
    request.headers["Expires"] = "0"
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request

app.config.update(
    FREEZER_IGNORE_404_NOT_FOUND=True
)

if __name__ == "__main__":
    app.run(debug=True)
