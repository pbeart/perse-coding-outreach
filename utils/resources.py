"Provide classes which represent a resources structure"

class ResourceFolder():
    "Represents a folder of resources"

    def __init__(self, contents, name, _id):
        self.id = _id
        self.name = name
        self.contents = contents
        assert(isinstance(x, Resource) for x in self.contents)

    def __str__(self, indent=0):
        "Return printable representation of resource folder structure"
        str_contents = "\n".join("\t"*indent + resource.__str__(indent=indent+1) for resource in self.contents)
        return "\t"*indent + f"{self.id}/{self.name}:\n" + str_contents

    def __repr__(self):
        "For debugging, return str of object"
        return str(self)

    def __getitem__(self, _id):
        "Get an item by id from the resource folder"
        try:
            return next(resource for resource in self.contents if resource.id == _id)
        except StopIteration as iteration_stopped:
            raise KeyError(f"Couldn't find sub-resource '{_id}'") from iteration_stopped

    def __contains__(self, _id):
        "Get if the folder contains an item with the specified id"
        return bool(any(resource for resource in self.contents if resource.id == _id))

    def get(self, _id, default=None):
        "Get an item from the resource folder with id 'id' or return default"
        if _id in self:
            return self[_id]
        else:
            return default

    def get_at_path(self, path):
        "Get the resource at the specified path in the folder"
        path_elements = [element for element in path.split("/") if element != ""]

        if len(path_elements) == 0:
            return self

        sub_resource = self[path_elements[0]]

        if isinstance(sub_resource, ResourceFolder) and len(path_elements) > 1:
            return sub_resource.get_at_path("/".join(path_elements[1:]))

        # Tried to access at a path beyond a non-folder
        if len(path_elements) > 1:
            raise KeyError("Tried to access at a resource path beyond a non-folder")

        return sub_resource

    def merged_with(self, other_folder):
        "Return a version of this folder merged with another folder"
        if other_folder is None:
            return self

        assert isinstance(other_folder, ResourceFolder)

        contents = []

        other_contents = other_folder.contents

        for resource in self.contents:

            # Potential conflict
            if resource.id in other_folder:
                other_resource = other_folder[resource.id]

                if isinstance(resource, ResourceFolder) and isinstance(other_resource, ResourceFolder):
                    contents.append(resource.merged_with(other_resource))
                    other_contents.remove(other_resource)
                else:
                    raise TypeError("Attempt to merge two resources, one of which is not a folder")
            else:
                contents.append(resource)

        for resource in other_contents:
            contents.append(resource)

        return ResourceFolder(contents, self.name, self.id)


class Resource():
    "Base class for a resource"
    def __init__(self, name, _id):
        self.name = name
        self.id = _id

class LinkResource(Resource):
    "A resource which points to a URL"
    def __init__(self, href, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.href = href

    def __str__(self, indent=0):
        return "\t"*indent + f"{self.id}/{self.name} link: {self.href}"

class FileResource(Resource):
    "A resource which points to a file path"
    def __init__(self, file_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = file_path

    def __str__(self, indent=0):
        return "\t"*indent + f"{self.id}/{self.name} file: {self.file_path}"

class HTMLResource(Resource):
    "A resource which has its own HTML content"
    def __init__(self, html, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.html = html

    def __str__(self, indent=0):
        return "\t"*indent + f"{self.id}/{self.name} html: {self.html[:10]}"
