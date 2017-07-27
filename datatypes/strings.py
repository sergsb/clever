from datatypes.base import PreferrableHDFDump, StringDatatype

class Smiles(StringDatatype):
    @property
    def preferrable_dump_to_hdf(self):
        return PreferrableHDFDump.AS_ATTRIBUTE

    def __init__(self,smiles):
        super(Smiles, self).__init__(smiles)

class Mol2(StringDatatype):
    @property
    def preferrable_dump_to_hdf(self):
        return PreferrableHDFDump.AS_ATTRIBUTE

    def __init__(self,mol2string):
        super(Mol2, self).__init__(mol2string)

class Prmtop(StringDatatype):
    @property
    def preferrable_dump_to_hdf(self):
        return PreferrableHDFDump.AS_ATTRIBUTE

    def __init__(self,prmtop_string):
        super(Prmtop, self).__init__(prmtop_string)

class Dx(StringDatatype):
    @property
    def preferrable_dump_to_hdf(self):
        return PreferrableHDFDump.NOT_SUPPORTED_YET

    def __init__(self,dx_string):
        super(Dx, self).__init__(dx_string)

class PDB(StringDatatype):

    @property
    def preferrable_dump_to_hdf(self):
        return PreferrableHDFDump.AS_ELEMENT_IN_DATASET

    @property
    def uff_energy(self):
        return self._uff_energy
    def __init__(self,pdbstring,uff_energy=None):
        super(PDB, self).__init__(pdbstring)
        self._uff_energy=uff_energy

