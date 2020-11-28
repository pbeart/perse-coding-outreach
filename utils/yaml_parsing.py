import yaml
from .resources import FileResource, ResourceFolder, LinkResource


def parse_resource_tree(struct, id, cpath):
    contents = []

    for key in struct:
        if key == "display_name":
            name = struct[key]

        sub_struct = struct[key]

        if "page_name" in sub_struct:
            contents.append(FileResource(name=sub_struct["page_name"],
                                         _id=key,
                                         file_path=cpath + "/" + key))

        elif "link_name" in sub_struct:
            contents.append(LinkResource(name=sub_struct["link_name"],
                                         _id=key,
                                         href=sub_struct["href"]))
                                        
        elif "display_name" in sub_struct:
            contents.append(parse_resource_tree(sub_struct, key, cpath + "/" + key))

    return ResourceFolder(name=name, _id=id, contents=contents)

def fetch_yaml_resources(path):
    "Read the content index file at path and return it as a ResourceFolder"

    with open(path, "r") as tree_file:
        struct = yaml.safe_load(tree_file)["resources"]

        return parse_resource_tree(struct, "resources", "resources")

