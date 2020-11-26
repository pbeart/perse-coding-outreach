"""Flask app to serve application so it can be frozen to static files.
Not particularly performant because it is never used in production"""

import os.path
import yaml
from bs4 import BeautifulSoup
import html2pdf

from flask import Flask, render_template, render_template_string, safe_join, abort, Response
app = Flask(__name__)

def parse_resource_tree():
    "Read the content-index.yaml file and return it as a dictionary"

    # This is inefficient but the site is static so it doesn't matter
    # so long as it doesn't make it unusable and it avoids any caching
    # problems

    with open("content-index.yaml", "r") as tree_file:
        struct = yaml.safe_load(tree_file)
        return struct

def get_resource_tree_value_at_path(path):
    """Return the structure or value at the path 'path' in the
    content-index.yaml structure"""
    path_elements = path.split("/")

    assert len(path_elements) > 0

    tree_dict = parse_resource_tree()

    path_element = path_elements[0]
    for path_element in path_elements:
        tree_dict = tree_dict[path_element]

    return {path_element: tree_dict}

def get_page_title(path):
    "Return the title of the page at the given path"
    path_elements = path.split("/")
    tree_dict = parse_resource_tree()

    for path_element in path_elements:
        tree_dict = tree_dict[path_element]

    return tree_dict["page_name"]

def get_path_urls_aliases_at_path(path):
    """Return a list of tuples containing url and display name for each
    stage in a path, like [('/folder/file', 'File'), ...],"""
    output = []

    path_elements = path.split("/")

    tree_dict = parse_resource_tree()

    for index, path_element in enumerate(path_elements):
        tree_dict = tree_dict[path_element]
        if "page_name" in tree_dict:
            name = tree_dict["page_name"]
        elif "display_name" in tree_dict:
            name = tree_dict["display_name"]

        output.append(["/"+"/".join(path_elements[:index+1]), name])

    return output

def generate_path_indicator(path):
    "Generate a list used to generate a path indicator from the given path"
    path_url_pairs = get_path_urls_aliases_at_path(path)
    return [["/", "Home"], *path_url_pairs]


def render_directory_listing(path):
    "Render a directory listing page for the given path."
    tree = get_resource_tree_value_at_path(path)

    if len(path.split("/")) > 1:
        base_path = "/" + "/".join(path.split("/")[:-1])
    else:
        # Avoid double / when appending url like /sub_page
        base_path = "/".join(path.split("/")[:-1])

    return render_template("resources_subsection.html",
                           tree=tree,
                           title=list(tree.values())[0]["display_name"],
                           base_url_path = base_path,
                           resource_path=generate_path_indicator(path))

@app.route('/')
def home():
    "Homepage"
    return render_template("index.html")

@app.route('/resources/<path:resource_name>/')
def resource(resource_name):
    "Fetch a resource"

    # Generate a safe path that cannot traverse above /resources
    safe_path = safe_join("resources", resource_name)

    # Show directory listing if it's a folder in the index
    
    try:
        structure = get_resource_tree_value_at_path(safe_path)
        if "display_name" in list(structure.values())[0]:
            return render_directory_listing(safe_path)

    # Index folder doesn't exist
    except KeyError:
        pass

        

    try:
        with open(safe_path + ".html") as resource_file:
            resource_content = render_template_string(resource_file.read())

            # Generate a list used in the contents template to generate
            # a contents page list of <h2> elements in the resource

            soup = BeautifulSoup(resource_content)
            headers = soup.find_all("h2")

            contents_list = []
            for header in headers:
                if header.get("id"):
                    contents_list.append([header.text, header["id"]])

            return render_template("resource.html",
                                   resource_html = resource_content,
                                   resource_path = generate_path_indicator(safe_path),
                                   resource_name = get_page_title(safe_path),
                                   contents_list = contents_list)
    except FileNotFoundError:
        abort(404)

@app.route('/resources/<path:resource_name>/printable.pdf')
def resource_pdf(resource_name):
    "Fetch a printable pdf version of a resource"

    safe_path = safe_join("resources", resource_name)

    try:
        with open(safe_path + ".html") as resource_file:
            resource_content = render_template_string(resource_file.read())

            # Generate a list used in the contents template to generate
            # a contents page list of <h2> elements in the resource

            soup = BeautifulSoup(resource_content)
            headers = soup.find_all("h2")

            contents_list = []
            for header in headers:
                if header.get("id"):
                    contents_list.append([header.text, header["id"]])

            template_html = render_template("resource.html",
                                            resource_html = resource_content,
                                            resource_path = generate_path_indicator(safe_path),
                                            resource_name = get_page_title(safe_path),
                                            contents_list = contents_list)

            return Response(html2pdf.html2pdf(template_html), mimetype="application/pdf")

    except FileNotFoundError:
        abort(404)

@app.route('/resources/')
def resources():
    "Root resources listing"
    return render_directory_listing("resources")


@app.errorhandler(404)
def not_found(_e):
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
