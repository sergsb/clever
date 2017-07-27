from functools import reduce

import time
from pebble import ProcessPool
from multiprocessing import cpu_count
from os.path import isdir, join, abspath
from glob import glob
import h5py
from datatypes.objects import Molecule, RISM
from operators.charges.ambercharges import AmberCharges
from operators.converters.select_top_conformer import SelectTopConformer
from operators.geometry.rdkitGeometry import RdKitGeometry
from operators.rism3d.rism3d import RISM3DCalculator
from processing.hdf5manage import lock_file, unlock_file, set_prefix, set_failed


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

class SelectTopAndCalcAmberCharges():
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        ch = AmberCharges(**kwargs)
        return ch(**(SelectTopConformer()(**kwargs)))

class RISMProcessor():
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        calc = RISM3DCalculator(kwargs['xvvfile'])
        pdbs = kwargs['pdbs']
        prmtop = kwargs['prmtop']
        collector = []
        for pdb in pdbs:
            collector.append(RISM(**calc(**{"pdb":pdb,"prmtop":prmtop})))
        rism =  reduce(lambda acc,rism: rism.merge(acc),collector,None)
        del collector
        kwargs.update({"rism":rism})
        return kwargs

extensions_dict = {"geometry": "???", "charges": "g??", "rism": "gc?"}
tmp_dict = {"geometry": "gzz", "charges": "gcz", "rism": "gcr"} #DelMe
locks_dict = {"geometry": "g", "charges": "c", "rism": "r"}
timeout_dict = {"geometry": 1200, "charges": 1200, "rism": 1200}
operators_dict = {"geometry":RdKitGeometry,
                  "charges":SelectTopAndCalcAmberCharges,
                  "rism":RISMProcessor}

def set_geometry_parser(root):
    geometry_parser = root.add_parser ( "geometry" )
    geometry_parser.add_argument ( '--number_of_conformers', type=int, required=True )
    geometry_parser.add_argument ( '--database', type=str, required=True )
    geometry_parser.set_defaults ( action='geometry' )

def set_charges_parser(root):
    charges_parser = root.add_parser ( "charges" )
    charges_parser.add_argument ( '--database', type=str, required=True )
    charges_parser.set_defaults (action='charges')

def set_rism_parser(root):
    rism_parser = root.add_parser ( "rism" )
    rism_parser.add_argument ( '--database', type=str, required=True )
    rism_parser.add_argument ( '--xvvfile', type=str, required=True)
    #rism_parser.add_argument ( '--number', type=int ) Not implemented yet
    rism_parser.set_defaults (action='rism')


def main_entrance_point(kwargs):
    #print(kwargs)
    file = kwargs['file']
    operator = operators_dict[kwargs['action']](**kwargs)
    file = lock_file(file,locks_dict[kwargs['action']])
    args = {}
    args.update(kwargs)
    #try:
    with h5py.File(file,'r+') as f:
        molecule = Molecule.load_from_hdf(f)
        args.update(molecule.data)
        molecule = Molecule(**operator(**args))
        molecule.dump_to_hdf(f)
    file = unlock_file ( file )
    set_prefix ( file, tmp_dict[kwargs['action']] )
    return None
    #except Exception as e:
    #    print(e)
    #    file = unlock_file (file)
    #    set_failed(file,locks_dict[kwargs['action']])




def process(**kwargs):
    assert isdir(kwargs['database'])
    path = join( kwargs['database'],"*{}.hdf".format( extensions_dict[kwargs['action']] ) )
    files = list(map(lambda file:abspath(file),glob(path)))
    assert len(files)>0
    args = list ( map ( lambda file: merge_dicts({'file':file},kwargs), files ) )
    with ProcessPool (max_workers=cpu_count()) as pool:
            future = pool.map( main_entrance_point, args, timeout=timeout_dict[kwargs['action']] )

    iterator = future.result ()
    while True:
        try:
            next(iterator)
        except StopIteration:
            break
        except TimeoutError as error:
            pass
            #print("function took longer than %d seconds" % error.args[1])
        time.sleep(0.5)
