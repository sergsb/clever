import shutil
import subprocess
import tempfile as tmp
import uuid
from os.path import join

from six import iteritems

from datatypes.strings import Dx
from envoronment.enviroment import get_global_environment
from operators.base import Operator


class RISM3DCalculator(Operator):
    def _parse_xvv_sites_names(self,data):
        def get_index_of_header(data,name):
            return list(map(lambda s: s[1:]==name,data)).index(True)

        splitted = data.split("\n")
        index_of_header = get_index_of_header(splitted,"FLAG ATOM_NAME")
        val = splitted[index_of_header+2]
        return val.split()

    def __init__(self, xvvfile=None, ng=70, solvcut=20, solvbox=35):
        self.ng = ng
        self.solvcut = solvcut
        self.solvbox = solvbox
        if xvvfile:
            self.xvvfile = xvvfile
        if not xvvfile and not self.xvvfile:
            raise Exception (
                "We need xvv file to perform 3D RISM calcualtion, please pass the path to the xvv file to RISM3DCalculator" )
        self.probings = self._parse_xvv_sites_names ( open ( xvvfile, 'r' ).read ( ) )
    def __call__(self, *args, **kwargs):
        pdb, prmtop = kwargs['pdb'].data,kwargs['prmtop'].data
        dir_path = tmp.mkdtemp ( )  # Create a temp directory for the calculation

        guv_name = str ( uuid.uuid4 ( ) )  # Create a uuid name for the output file
        # uuv_name = str(uuid.uuid4())  # Create a uuid name for the output file
        # cuv_name = str(uuid.uuid4())  # Create a uuid name for the output file

        input_pdb_file = tmp.NamedTemporaryFile ( dir=dir_path, suffix='.pdb',
                                                  delete=False ,mode='w')  # Create a temp input file int the temp directory for the calculation
        input_pdb_file.write ( pdb )
        input_pdb_file.flush ( )

        input_prmtop_file = tmp.NamedTemporaryFile ( dir=dir_path, suffix='.prmtop',
                                                     delete=False,mode='w' )  # Create a temp input file int the temp directory for the calculation
        input_prmtop_file.write ( prmtop )
        input_prmtop_file.flush ( )

        params_dict = {'pdb': input_pdb_file.name,
                       'prmtop': input_prmtop_file.name,
                       'xvv': self.xvvfile,
                       'ng': ",".join ( [str ( self.ng )] * 3 ),
                       'solvcut': str ( self.solvcut ),
                       'solvbox': ",".join ( [str ( self.solvbox )] * 3 ),
                       'buffer': str ( -1 ),
                       'guv': guv_name
                       #              'uuv': uuv_name,
                       #              'cuv': cuv_name
                       }

        param_line = [join(get_global_environment()['AMBERHOME'],"bin","rism3d.snglpnt")]  # We use program name

        for (k, v) in iteritems(params_dict):
            param_line.append ( '--' + k )
            param_line.append ( v )
        try:
            subprocess.check_output ( param_line, cwd=dir_path,env=get_global_environment())
        except subprocess.CalledProcessError as e:
            raise RuntimeError (
                "command '{}' return with error (code {}): {}".format ( e.cmd, e.returncode, e.output ) )


        path_to_guv_files = join ( dir_path, guv_name )
        # path_to_uuv_files = join(dir_path, uuv_name)
        # path_to_cuv_files = join(dir_path, cuv_name)

        guv = {"guv_probing_%s" % probing: Dx(open( path_to_guv_files + ".%s.1.dx" % probing ,'r').read()) for probing in
               self.probings}
        input_prmtop_file.close ( )
        input_pdb_file.close ( )

        shutil.rmtree ( dir_path )  # BE VARY CAREFULL TO MODIFY IT!
        union = {}
        union.update ( guv )
        # union.update(uuv)
        # union.update(cuv)
        kwargs.update ( {"rism3ddx": union} )
        return kwargs