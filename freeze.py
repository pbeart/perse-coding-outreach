from flask_frozen import Freezer
from app import app as flask_app
import app
import yaml

from utils import resources

freezer = Freezer(flask_app)

def generate_urls(tree, path):

    out = []

    for resource in tree.contents:
        if isinstance(resource, resources.HTMLResource) or isinstance(resource, resources.FileResource):
            out.append(path + "/" + resource.id + "/")
        elif isinstance(resource, resources.ResourceFolder):
            out.append(path + "/" + resource.id + "/")
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