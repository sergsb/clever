import shutil
import subprocess
import tempfile as tmp
import uuid
from os.path import join

from datatypes.strings import Mol2, PDB, Prmtop
from envoronment.enviroment import get_global_environment


class AmberCharges:
    leapscript = """source {leaprc}
        mol = loadmol2 "{name}.mol2"
        check mol
        loadamberparams "{name}.frcmod"
        SaveAmberParm mol "{name}.prmtop" "{name}.incrd"
        SavePdb mol "{name}.pdb"
        quit
        """

    def __init__(self, *args,**kwargs): #charge_model='bcc', lj='gaff2', minimize=False, moltype='pdb', molcharge=0, multiplicity=1):
        self.charge_model = kwargs['charge_model'] if 'charge_model' in kwargs else 'bcc'
        self.lj = kwargs['lj'] if 'lj' in kwargs else 'gaff2'
        self.minimize = kwargs['minimize'] if 'minimize' in kwargs else False
        self.moltype = kwargs['moltype'] if 'moltype' in kwargs else 'pdb'
        self.molcharge = 0
        self.multiplicity = 1
        if self.lj == 'gaff2':
            self.at = self.lj
        else:
            self.at = 'gaff'

    def __call__(self,*args, **kwargs):
        input_pdb = kwargs["pdb"].data
        # print "Molecule is: %s " % string
        dir_path = tmp.mkdtemp()  # Create a temp directory for the calculation

        input_file = tmp.NamedTemporaryFile(dir=dir_path,
                                            mode='w',
                                            delete=False)  # Create a temp input file int the temp directory for the calculation
        input_file.write(input_pdb)
        input_file.close()

        output_filename = uuid.uuid4()
        try:
            subprocess.check_output([join(get_global_environment()['AMBERHOME'],"bin","antechamber"),
                                 '-i', input_file.name,
                                 '-fi', self.moltype,
                                 '-at', self.at,
                                 '-o', '{}.mol2'.format(output_filename),  # output file
                                 '-fo', 'mol2',  # output format    describing each residue
                                 '-c', self.charge_model,  # charge method (AM1-BCC)
                                 '-s', '2',  # status info ; 2 means verbose
                                 '-nc', str(self.molcharge),  # Net molecule charge
                                 '-m', str(self.multiplicity)  # Multiplicity
                                 ], cwd=dir_path,env=get_global_environment())
        except subprocess.CalledProcessError as e:
            raise RuntimeError ( "command '{}' return with error (code {}): {}".format ( e.cmd, e.returncode, e.output ) )

        try:
            subprocess.check_output([join(get_global_environment()['AMBERHOME'],"bin","parmchk2"),
                                     '-i', '{}.mol2'.format(output_filename),
                                     '-f', 'mol2',
                                     '-o', '{}.frcmod'.format(output_filename)],  # file with missing FF params
                                    cwd=dir_path,env=get_global_environment())
        except subprocess.CalledProcessError as e:
            raise RuntimeError (
                "command '{}' return with error (code {}): {}".format ( e.cmd, e.returncode, e.output ) )

        # Run tleap to generate topology and coordinates for the molecule
        if self.lj == 'gaff2':
            leaprc = 'leaprc.gaff2'
        else:
            leaprc = 'leaprc.gaff'
        leap_input_name = join(dir_path, 'runleap.in')

        with open(leap_input_name, 'w') as f:
            f.write(self.leapscript.format(name=output_filename, leaprc=leaprc))

        try:
            subprocess.check_output([join(get_global_environment()['AMBERHOME'],"bin/tleap"), '-f', 'runleap.in'], cwd=dir_path,env=get_global_environment())
        except subprocess.CalledProcessError as e:
            raise RuntimeError (
                "command '{}' return with error (code {}): {}".format ( e.cmd, e.returncode, e.output ) )

        try:
            output_pdb = open(join(dir_path, '{}.pdb'.format(output_filename)), 'r').read()
            output_prmtop = open(join(dir_path, '{}.prmtop'.format(output_filename)), 'r').read()
            output_mol2 = open(join(dir_path, '{}.mol2'.format(output_filename)), 'r').read()
            kwargs.update({"prmtop":Prmtop(output_prmtop), "mol2":Mol2(output_mol2), "pdb":PDB(output_pdb)})

            shutil.rmtree(dir_path)  # BE VARY CAREFULL TO MODIFY IT!
            return kwargs
        except Exception as e:
            raise Exception(e)
