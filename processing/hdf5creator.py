import os
from os.path import splitext, basename, abspath, dirname, join
import h5py
import logging
# noinspection PyUnresolvedReferences
from rdkit import Chem
from datatypes.objects import Properties, Molecule
from datatypes.strings import Smiles

def set_createdb_parser(root):
    createdb = root.add_parser ( "createdb" )
    createdb.set_defaults ( action='createdb' )
    createdb.add_argument ( '--file', type=str, help="An sdf file with molecules",required=True)
    createdb.add_argument ( '--properties', type=str, nargs='+', help="The properties for prediction",required = True)
    createdb.add_argument ( '--output', type=str,help="A path to the database created",required=True)


def create_hdf_database(**kwargs):
    assert kwargs['properties']
    if kwargs['output']:
        _output_ = kwargs['output']
        base = _output_
    else:
        base = splitext ( basename ( kwargs['file'] ) )[0]
        rundir = dirname ( abspath ( __file__ ) )
        _output_ = join ( rundir, base )

    try: os.mkdir ( _output_ )
    except: pass
    suppl = Chem.SDMolSupplier ( kwargs['file'] )
    mol_and_prop = [(mol,{prop_name:mol.GetProp ( prop_name )for prop_name in kwargs['properties']}) for mol in suppl]
    total = len ( mol_and_prop )
    logging.info ( "Readed: {} molecules from: {} with property {}"
                   .format ( total, kwargs['file'] , kwargs['properties']  ) )
    for i in range ( total ):
        with h5py.File ( join ( _output_, '{}_{}_zzz.hdf'.format ( base, i ) ), 'w' ) as f:
            logging.info ( "Creating file: {}_{}_zzz.hdf".format ( base, i ) )
            rdkit_mol, prop = mol_and_prop[i]
            rdkit_mol = Chem.AddHs ( rdkit_mol )
            prop = Properties(**{"properties":prop})
            smiles = Smiles(Chem.MolToSmiles ( rdkit_mol, isomericSmiles=True ))
            mol = Molecule(**{"smiles":smiles,"properties":prop})
            mol.dump_to_hdf(f)