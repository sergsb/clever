import numpy as np
from builtins import map

from six import StringIO


class VolToDx():
    s = StringIO()
    str ="""object 1 class gridpositions counts {xlen} {ylen} {zlen}
origin    {OrX} {OrY} {OrZ}
delta  {dX} 0 0
delta  0 {dY} 0
delta  0 0 {dZ}
object 2 class gridconnections counts {xlen} {ylen} {zlen}
object 3 class array type double rank 0 items {length} data follows
{records}
    """
    def __init__(self):
        pass
    def __call__(self, *args, **kwargs):
        volume = kwargs['volume']
        xlen,ylen,zlen = volume.shape
        try:
            (OrX, OrY, OrZ) = kwargs['origin']
            (dX, dY, dZ) = kwargs['dsteps']
        except:
            raise NotImplementedError() #FixMe: !!!

        assert type(volume) == np.ndarray
        length = np.prod(volume.shape)
        #print(locals()['xlen'])
        records = ""
        flatten = volume.flatten()
        for i in range(1,length+1):
            records += str(flatten[i-1]) + " "
            if i % 3 == 0 and i!=length: records += "\n"
        #records = np.savetxt(self.s,volume.reshape(3,-1),delimiter=" ")
        list_of_variables = ["xlen","ylen","zlen","OrX", "OrY", "OrZ","dX","dY","dZ","length","records"]
        params = {}
        for k in list_of_variables: params[k] = locals()[k]
#        print(params)
        return self.str.format(**params)

class DxToVol():

    def _load_dx(self, string):
        """
            Return dx matrix, origin coordinates tuple and spacing between points tuple.
        """
        string = string.split("\n")
        if string[0].startswith('object 1 class gridpositions counts'):
            size = string[0][35:].split()
            size = list(map(int, size))
        else:
            print('Wrong file format') #FixMe: Correct error handling
            raise ValueError
        dx_m = []
        for line in string:
            ln = line.split()
            if len(ln) <= 3:
                dx_m.extend(ln)
            elif (ln[0] == 'origin'):
                OrX = float(ln[1])
                OrY = float(ln[2])
                OrZ = float(ln[3])
            elif (ln[0] == 'delta' and ln[1] != '0'):
                dX = float(ln[1])
            elif (ln[0] == 'delta' and ln[2] != '0'):
                dY = float(ln[2])
            elif (ln[0] == 'delta' and ln[3] != '0'):
                dZ = float(ln[3])
        dx_m = np.array(dx_m)
        dx_m = dx_m.reshape(size)
        return dx_m.astype('float'), (OrX, OrY, OrZ), (dX, dY, dZ)

    def __call__(self, *args, **kwargs):
        string = args[0]
        volumes, origins,dsteps = self._load_dx(string)
        return {"volume":volumes,"origin":origins,"dsteps":dsteps}

