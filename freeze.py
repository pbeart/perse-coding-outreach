from flask_frozen import Freezer
from app import app as flask_app
import app
import yaml
from utils import gdrive_parsing
import urllib
from utils import resources

freezer = Freezer(flask_app)

def quote_plus_url(url):
        "Take a url with pre-urlencoded segments and give it another round of urlencoding"
        return "/".join(urllib.parse.quote_plus(seg) for seg in url.split("/"))

def generate_urls(tree, path):

    out = []

    # We have to call quote_plus_url twice because frozen flask will attempt to de-urlencode the paths

    for resource in tree.contents:
        if isinstance(resource, resources.HTMLResource) or isinstance(resource, resources.FileResource):
            out.append(app.quote_plus_url(app.quote_plus_url(path + "/" + resource.id + "/")))
        elif isinstance(resource, resources.ResourceFolder):
            out.append(app.quote_plus_url(app.quote_plus_url(path + "/" + resource.id + "/")))
            out += generate_urls(resource, path + "/" + resource.id)
    return out

@freezer.register_generator
def generate_resources():
    tree = app.all_resources
    return generate_urls(tree, "/resources")

@freezer.register_generator
def generate_404():
    return ["/404.html"]

if __name__ == '__main__':
    freezer.freeze()