from flask_frozen import Freezer
from app import app as flask_app
import app
import yaml

freezer = Freezer(flask_app)

def generate_urls(tree, path):

    out = []

    for key in tree:
        value = tree[key]

        if not isinstance(value, dict):
            continue

        if "page_name" in value:
            out.append(path + "/" + key + "/")
            out.append(path + "/" + key + "/printable.pdf")
        else:
            out.append(path + "/" + key + "/")
            out += generate_urls(value, path + "/" + key)
    return out

@freezer.register_generator
def resources():
    tree = app.parse_resource_tree()
    return generate_urls(tree, "")



if __name__ == '__main__':
    freezer.freeze()