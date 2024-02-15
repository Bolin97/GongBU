from .llm_app import LLMApp
import os
import shutil
import importlib

# an app is a folder
# it has an entry.py that contains a Main class that can be converted to LLMApp class

# returns a list of classes
def scan() -> list[any]:
    # check if path is a folder
    ret = []
    # iterate over the folders in the folder
    for folder in os.listdir("backend/ext"):
        # check if the folder has an entry.py
        if folder.startswith("_"):
            continue
        if os.path.isfile(os.path.join("backend/ext", folder, "entry.py")):
            # import the module
            module = importlib.import_module(f"backend.ext.{folder}.entry")
            # get the Main class
            try:
                ret.append(module.Main)
            except AttributeError:
                pass
    return ret