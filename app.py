import os.path
import yaml
from bs4 import BeautifulSoup

from flask import Flask, render_template, render_template_string, safe_join, abort, url_for
app = Flask(__name__)

def parse_resource_tree():
    with open("content-index.yaml", "r") as f:
        struct = yaml.safe_load(f)
        return struct

def get_resource_tree_value_at_path(path):
    path_elements = path.split("/")

    tree_dict = parse_resource_tree()



    for el in path_elements:
        tree_dict = tree_dict[el]

    return {el: tree_dict}

def get_page_title(path):
    path_elements = path.split("/")
    tree_dict = parse_resource_tree()

    for el in path_elements:
        tree_dict = tree_dict[el]

    return tree_dict["page_name"]

def get_path_urls_aliases_at_path(path):
    output = []

    path_elements = path.split("/")

    tree_dict = parse_resource_tree()

    for index, el in enumerate(path_elements):
        tree_dict = tree_dict[el]
        print(index, el, tree_dict, path_elements[:index+1])
        if "page_name" in tree_dict:
            name = tree_dict["page_name"]
        elif "display_name" in tree_dict:
            name = tree_dict["display_name"]

        output.append(["/"+"/".join(path_elements[:index+1]), name])
        

    return output

def generate_path_indicator(path):
    path_url_pairs = get_path_urls_aliases_at_path(path)  
    return [["/", "Home"], *path_url_pairs]


def render_directory_listing(path):
    tree = get_resource_tree_value_at_path(path)

    if len(path.split("/")) > 1:
        base_path = "/" + "/".join(path.split("/")[:-1])
    else:
        base_path = "/".join(path.split("/")[:-1]) # Avoid double / when appending url like /sub_page
    
    print("Using base path")
    print(base_path)

    return render_template("resources_subsection.html",
                           tree=tree,
                           title=list(tree.values())[0]["display_name"],
                           base_url_path = base_path,
                           resource_path=generate_path_indicator(path))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/resources/<path:resource_name>')
def resource(resource_name):

    safe_path = safe_join("resources", resource_name)

    # Show directory listing
    if os.path.isdir(safe_path):
        return render_directory_listing(safe_path)

    try:
        with open(safe_path + ".html") as f:

            resource_content = render_template_string(f.read())

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

@app.route('/resources/')
def resources():
    return render_directory_listing("resources")


@app.errorhandler(404)
def not_found(e): 
    return render_template('404.html'), 404

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == "__main__":
    app.run(debug=True)
