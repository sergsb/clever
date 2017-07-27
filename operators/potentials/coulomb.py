import numpy as np
import cupy
from builtins import map

class Coulomb( ):
    def _parseMol2(self, mol2string):
        def find_between(s, first, last):
            try:
                start = s.index ( first ) + len ( first )
                end = s.index ( last, start )
                return s[start:end]
            except ValueError:
                return ""

        def process_symbol(symbol):
            '''
            remove digits from the atom symbol i.e. C11 -> C
            :param symbol: raw symbol
            :return: purified symbol
            '''
            res = []
            for s in symbol[::-1]:
                if s not in list(map ( lambda n: str ( n ), range ( 0, 10 ) )):
                    res.append ( s )
            return "".join ( res[::-1] )

        data = mol2string
        atoms = find_between ( data, "@<TRIPOS>ATOM\n", "\n@<TRIPOS>BOND" ).split ( '\n' )
        atoms = list(map ( lambda s: (int ( s.split ( )[0] ),
                                 s.split ( )[1], s.split ( )[5],
                                 list(map ( lambda i: float ( i ), s.split ( )[2:5] )),
                                 float ( s.split ( )[-1] )), atoms ))
        return atoms

    def _parsePdb(self, pdb_string):
        lines = pdb_string.split ( "\n" )
        lines = list(filter(lambda s:s.startswith("ATOM"),lines))
        checkpoint = [(int ( line.split ( )[1] ), line.split ( )[2]) for line in lines]
        parsed = {
        line.split ( )[2]: [float ( line.split ( )[5] ), float ( line.split ( )[6] ), float ( line.split ( )[7] )] for
        line in lines}
        assert len ( parsed ) == len ( lines )
        return parsed, checkpoint

    def _exchange_coordinates(self,structure, parsed_pdb):
        parsed, checkpoint_pdb = parsed_pdb
        mol2_checkpoint = list(zip(list(zip(*structure))[0], list(zip(*structure))[1]))
        assert mol2_checkpoint == checkpoint_pdb
        modified = []
        for atom in structure:
            modified.append((atom[0], atom[1], atom[2], parsed[atom[1]], atom[4]))
        return modified

    def __init__(self, cube_length=35., grid=0.5,use_gpu=True):
        self.cube_length = cube_length
        self.grid = grid
        self.use_gpu = use_gpu
        line = np.linspace(-cube_length / 2., cube_length / 2., cube_length / grid,dtype=np.float32)
        c = np if not self.use_gpu else cupy
        self.probings = np.array(np.meshgrid(line, line, line,sparse=False),dtype=np.float32).T.reshape(-1, 3)
        self.probings[:,[0,1,2]] = self.probings[:,[2,0,1]]
        self.probings = c.array(self.probings)
#0,1,2 -
#0,2,1 !
#1,0,2 -
#1,2,0 -
#2,0,1 !
#2,1,0 -


    def __call__(self, *args, **kwargs):
        mol2_string = kwargs['mol2'].data
        pdb_string = kwargs['pdb'].data if 'pdb' in list(kwargs) else None
        if not pdb_string:
            structure = self._parseMol2(mol2_string)
        else:
            structure = self._exchange_coordinates(self._parseMol2(mol2_string),self._parsePdb(pdb_string))

        atoms = np.array(list(map(lambda atom: np.hstack((atom[3], np.array(atom[4]))), structure)))
        c = np if not self.use_gpu else cupy
        atoms = c.array(atoms,dtype=np.float32)
        r_gpu = c.zeros((len(atoms),len(self.probings)),dtype=np.float32)
        for i, charge_of_atom_in_interest in zip(range(len(atoms)), atoms[:, 3]):
            r_gpu[i]  = (1./(c.linalg.norm((self.probings - atoms[i,:3]),axis=1)))*charge_of_atom_in_interest
        gpu_coulomb = c.sum(r_gpu, axis=0).reshape(70, 70, 70)
        volume = c.asnumpy(gpu_coulomb) if self.use_gpu else gpu_coulomb
        origin = [-(self.cube_length/2.)]*3
        dsteps = [self.grid]*3
        return kwargs.update({"volume":volume,"origin":origin,"dsteps":dsteps})