import h5py
import numpy as np
from six import iteritems

from datatypes.base import PreferrableHDFDump, Datatype
from datatypes.strings import PDB, Smiles, Prmtop, Mol2
from operators.converters.vol_dx import DxToVol

class Properties(Datatype):
    strtype = h5py.special_dtype ( vlen=bytes )
    def __init__(self,**kwargs):
        assert kwargs != {}
        self.data = kwargs["properties"]

    def preferrable_dump_to_hdf(self):
        return PreferrableHDFDump.I_DO_IT_SELF
    def dump_to_hdf(self,f):
        if 'Properties' not in f:
            g = f.create_group("/Properties")
            ordered = sorted ( self.data.keys ( ) )
            values = np.zeros(shape=(1,len(self.data.values()))) # The format convenient to chainer format
            for i,k in zip(range(len(ordered)),ordered):
                values[i] = self.data[k]
            g.create_dataset("X",data=values)
            g.create_dataset("labels",data=list(map(lambda s:s.encode(),ordered)))

    @staticmethod
    def load_from_hdf(f):
        return {"properties":{k:v for v,k in zip(f['Properties/X'][:],f['Properties/labels'][:])}}


class RISM( Datatype ):
    dx2vol = DxToVol()
    strtype = h5py.special_dtype ( vlen=bytes )
    def dump_to_hdf(self,f):
        rism_group = f.create_group("/RISM")
        rism_group.create_dataset('X',data=self.RISM,dtype=np.float32)
        rism_group.create_dataset('origins', data=self.origins, dtype=np.float32 )
        rism_group.create_dataset('dsteps', data=self.dsteps, dtype=np.float32 )
        rism_group.create_dataset('mapping', data=[s.encode() for s in self.mapping],dtype=self.strtype)

    def load_from_hdf(self,f):
        self.RISM = f['/RISM/X']
        self.origins = f['/RISM/origins']
        self.dsteps = f['/RISM/dsteps']
        self.mapping = f['/RISM/mapping']
        return self

    @property
    def preferrable_dump_to_hdf(self):
        return PreferrableHDFDump.I_DO_IT_SELF

    def __init__(self,**dx_files):
         dx = dx_files['rism3ddx']
         volumes = {name:self.dx2vol(dx_object.data) for name,dx_object in iteritems(dx)}

         arrays = list(map ( lambda d: d['volume'].shape,volumes.values()))

         length = len ( arrays )
         assert len ( set ( arrays ) ) == 1

         RISM = np.zeros ( (1,length, arrays[0][0], arrays[0][1], arrays[0][2]), dtype=np.float32 )
         origins = np.zeros ((1,length, 3), dtype=np.float32 )
         dsteps = np.zeros ((1,length, 3), dtype=np.float32 )


         ordered = sorted ( volumes.keys() )

         for i in range ( length ):
             RISM[0][i] = volumes[ordered[i]]['volume']
             origins[0][i] = volumes[ordered[i]]['origin']
             dsteps[0][i] = volumes[ordered[i]]['dsteps']

         self.RISM = RISM
         self.origins = origins
         self.dsteps = dsteps
         self.mapping = ordered

    def merge(self, other):
        if isinstance( other, RISM ):
            self.RISM = np.vstack((self.RISM,other.RISM))
            self.origins = np.vstack((self.origins,other.origins))
            self.dsteps = np.vstack ( (self.dsteps, other.dsteps) )
            self.mapping = self.mapping + other.mapping
            return self
        elif other == None: return self
        else: raise BaseException("Type of another object is not RISM")

class PDBS( Datatype ):
    strtype = h5py.special_dtype ( vlen=bytes )

    @property
    def preferrable_dump(self):
        return PreferrableHDFDump.I_DO_IT_SELF

    def dump_to_hdf(self,f):
        if 'PDBS' not in f:
            g = f.create_group("/PDBS")
            g.create_dataset('X',data=[s.data.encode() for s in self.data],dtype=self.strtype)
            g.create_dataset('uff_energy',data=[s.uff_energy for s in self.data],dtype=np.float32)

    @staticmethod
    def load_from_hdf(f):
        return {'pdbs':PDBS( pdbs = list( map ( lambda s:PDB( s[0].decode( ), uff_energy=s[1] ), list( zip( f['/PDBS/X'][:], f['/PDBS/uff_energy'][:] ) ) ) ) )}

    def __iter__(self):
        return iter(self.data)

    def __init__(self,**pdbs):
        self.data = pdbs['pdbs']


attrs_mapping  = {"smiles":Smiles,"prmtop":Prmtop,"mol2":Mol2}
groups_mapping = {"PDBS":PDBS,"Properties":Properties}

class Molecule(object):

    def __init__(self,*args,**kwargs):
        assert kwargs != {}
        self.data = kwargs

    @staticmethod
    def load_from_hdf(f):
        collector = {}
        for attr in f.attrs:
            if attr in attrs_mapping:
                collector.update({attr:attrs_mapping[attr](f.attrs[attr])})
        for key in f.keys():
            collector.update(groups_mapping[key].load_from_hdf(f))
        return Molecule(**collector)

    def dump_to_hdf(self,f):
        for k,v in iteritems(self.data):
            if isinstance(v,Datatype):
                v.dump_to_hdf( f )
