import operator
import random

import datatypes
from datatypes.objects import PDBS
from datatypes.strings import Smiles, PDB
from operators.base import Operator, get_short_name_for_type
# noinspection PyUnresolvedReferences
from rdkit import Chem
# noinspection PyUnresolvedReferences
from rdkit.Chem import AllChem
# noinspection PyUnresolvedReferences
from rdkit.Chem import rdMolTransforms as rdmt

from operators.converters.rdkit2amberpdb import rdkit2amberpdb


class RdKitGeometry(Operator):

    def _rdkit_calc_energy_uff(self,mol, conformerId, minimizeIts):
        ff = AllChem.UFFGetMoleculeForceField ( mol, confId=conformerId )
        # ff.Initialize()
        results = {}
        if minimizeIts > 0:
            results["converged"] = ff.Minimize ( maxIts=minimizeIts )
        results = ff.CalcEnergy ( )
        return results

    loaders = {'smiles':Chem.MolFromSmiles,'pdb':Chem.MolFromPDBBlock}
    input_formats = set([k for k in loaders])

    def __init__(self, *args,**kwargs):
        self.n = kwargs['number_of_conformers']
        self.pre_rmsThresh = 1.#pre_rmsThresh
        self.rmsThresh = 0.5#rmsThresh
        self.orientatePCA = True#orientatePCA

    def __call__(self,*args,**kwargs):
        input = set([k for k in kwargs]).intersection(self.input_formats)
        assert len(input) == 1
        typename = list(input)[0]
        data = kwargs[typename]
        molecule = self.loaders[typename](data.data)
        molecule = Chem.AddHs ( molecule )
        confIds = AllChem.EmbedMultipleConfs ( molecule, self.n * 4, maxAttempts=10000, pruneRmsThresh=self.pre_rmsThresh )

        for conf in confIds:
            AllChem.UFFOptimizeMolecule ( molecule, maxIters=5000, confId=conf )

        energies = []
        for conf in confIds:
            energies.append ( (conf, self._rdkit_calc_energy_uff ( molecule, conf, 0 )) )

        conformers_ids = list(map ( lambda x: x[0], sorted ( list ( energies ), key=operator.itemgetter ( 1 ) ) ))
        before = len ( conformers_ids )  # Conformers we have in total

        if before < self.n:
            selected = conformers_ids
        else:
            c_keep = [conformers_ids[0]]
            conformers_ids = conformers_ids[1:]
            for conf in conformers_ids:
                good = True
                for conf_in_c_keep in c_keep:
                    rms = AllChem.GetConformerRMS ( molecule, conf, conf_in_c_keep, prealigned=False )
                    if rms < self.rmsThresh:
                        good = False
                        break
                if good:
                    c_keep.append ( conf )
            selected = c_keep

            if len ( selected ) >= self.n:
                selected = random.sample ( selected, self.n )

        list(map ( lambda i: rdmt.CanonicalizeConformer ( molecule.GetConformer ( i ) ), selected ))

        energies = []
        for conf in selected:
            energies.append ( (conf, self._rdkit_calc_energy_uff ( molecule, conf, 0 )) )
        selected = list(sorted ( list ( energies ), key=operator.itemgetter ( 1 ) ) )


        mol_conformers = map (
            lambda s: (Chem.MolFromPDBBlock (
                Chem.MolToPDBBlock ( molecule, confId=s[0] ), sanitize=False, removeHs=False ),
                              s[1],)
            ,selected)

        pdbs = [(PDB(rdkit2amberpdb(Chem.MolToPDBBlock(mol_conformer)),uff_energy=energy)) for mol_conformer,energy in mol_conformers]
        kwargs.update( {"pdbs": PDBS( pdbs=pdbs )} )
        return kwargs