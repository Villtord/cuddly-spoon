"""
This type stub file was generated by pyright.
"""

"""
    This is the h5py completer extension for ipython.  It is loaded by
    calling the function h5py.enable_ipython_completer() from within an
    interactive IPython session.

    It will let you do things like::

      f=File('foo.h5')
      f['<tab>
      # or:
      f['ite<tab>

    which will do tab completion based on the subgroups of `f`. Also::

      f['item1'].at<tab>

    will perform tab completion for the attributes in the usual way. This should
    also work::

      a = b = f['item1'].attrs.<tab>

    as should::

      f['item1/item2/it<tab>
"""
re_attr_match = ...
re_item_match = ...
re_object_match = ...
def h5py_item_completer(context, command): # -> list[Any] | list[str]:
    """Compute possible item matches for dict-like objects"""
    ...

def h5py_attr_completer(context, command): # -> list[Any] | list[str]:
    """Compute possible attr matches for nested dict-like objects"""
    ...

def h5py_completer(self, event): # -> list[Any] | list[str]:
    """ Completer function to be loaded into IPython """
    ...

def load_ipython_extension(ip=...): # -> None:
    """ Load completer function into IPython """
    ...
