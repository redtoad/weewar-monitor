# A resource  module which you can import for loading resources such as images,
# fonts, or whatever you want.
# by Martin Grimme (with small adjustments by me)
# http://pycage.blogspot.com/2007/12/tablet-python-2-resource-modules.html

import os
import gtk

_RESOURCE_PATH = os.path.dirname(__file__)

def _load_resources():

    # Find all .png files in the resource directory. This construct is called
    # "list comprehension" and will be covered in detail in episode #3.
    # This returns a list of the names of all files in the resource directory
    # ending with ".png".
    resources = [f for f in os.listdir(_RESOURCE_PATH)]
                    
    # load resources into module namespace
    for r in resources:

        # the filename without extension will be the name to access the
        # resource, so we strip off the extension
        name, ext = os.path.splitext(r)
          
        # this is the full path to the resource file
        path = os.path.join(_RESOURCE_PATH, r)
          
        # Now we can load the resource into the module namespace.
        # globals() gives us the dictionary of the module-global variables,
        # and we can easily extend it by assigning new keys.
        try:
            globals()[name] = {
                '.gif' : gtk.gdk.pixbuf_new_from_file,
                '.glade' : gtk.glade.XML,
            }[ext](path)
        except KeyError:
            pass

    #end for

# load the resources when importing the module
_load_resources()
