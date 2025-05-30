"""
This type stub file was generated by pyright.
"""

from .base import HLObject, with_phil

"""
    Implements high-level access to committed datatypes in the file.
"""
class Datatype(HLObject):
    """
        Represents an HDF5 named datatype stored in a file.

        To store a datatype, simply assign it to a name in a group:

        >>> MyGroup["name"] = numpy.dtype("f")
        >>> named_type = MyGroup["name"]
        >>> assert named_type.dtype == numpy.dtype("f")
    """
    @property
    @with_phil
    def dtype(self):
        """Numpy dtype equivalent for this datatype"""
        ...
    
    @with_phil
    def __init__(self, bind) -> None:
        """ Create a new Datatype object by binding to a low-level TypeID.
        """
        ...
    
    @with_phil
    def __repr__(self): # -> LiteralString | Literal['<Closed HDF5 named type>']:
        ...
    
