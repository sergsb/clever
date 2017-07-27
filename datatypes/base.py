from abc import ABCMeta, abstractmethod
from enum import Enum
import numpy as np

class PreferrableHDFDump( Enum ):
    AS_ATTRIBUTE = 1
    AS_ELEMENT_IN_DATASET = 2
    NOT_SUPPORTED_YET = 3
    I_DO_IT_SELF = 4

class Datatype(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def dump_to_hdf(self, h):
        pass

    @abstractmethod
    def dump_to_hdf_as_attribute(self, h):
        """
        :param h: A handle for HDF5 file to save
        :return: None
        """
        pass
    @property
    def preferrable_dump_to_hdf(self):
        pass


class StringDatatype(Datatype):
    def __init__(self,string):
        self.data = string

    def __repr__(self):
        return self.data

    def dump_to_hdf(self, h):
        if self.preferrable_dump_to_hdf == PreferrableHDFDump.AS_ATTRIBUTE:
            self._dump_as_attribute(h)
    def _dump_as_attribute(self,h):
        h.attrs[self.__class__.__name__.lower()] = self.__repr__()

'''
class Array(list):
    @property
    def _internal_types(self):
        return [t.__class__.__name__ for t in self]
    def _internal_type_check(self):
        assert len(set(self._internal_types)) == 1
#        super(Array, self).__add__(other)
    def dump(self,h,strategy="override"):
        self._internal_type_check()
        baseclass = self.__getitem__(0).__class__
        baseclass_name = baseclass.__name__
        #print(str(baseclass.preferrable_dump))
        #assert baseclass.preferrable_dump == PreferrableHDFDump.AS_ELEMENT_IN_DATASET
        if (strategy == "add") and (baseclass_name in h):
            print("here")
            X = h[baseclass_name]["X"][:].copy()
            del h[baseclass_name]["X"]
            h[baseclass_name].create_dataset("X", data=np.vstack((X,self)))
            h.flush()
            return None

        elif (strategy == "override") and (baseclass_name in h):
            del h[baseclass_name]["X"]
            del h[baseclass_name]

        g = h.create_group(baseclass_name)
        g.create_dataset("X", data=self)
'''

class VolumeDatatype(Datatype,np.ndarray):
    def __init__(self,data):
        super(VolumeDatatype, self).__init__(data)
    @property
    def preferrable_dump_to_hdf(self):
        return PreferrableHDFDump.AS_ELEMENT_IN_DATASET

'''

class Float32Datatype(Datatype):
    pass

class VariableLenghtDatatype(Datatype):
    pass
'''