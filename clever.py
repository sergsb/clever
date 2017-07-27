import argparse
from processing.hdf5creator import create_hdf_database, set_createdb_parser
from processing.core import set_geometry_parser, process, set_charges_parser, set_rism_parser

functions = {"createdb":create_hdf_database,"geometry":process,"charges":process,"rism":process}

parser = argparse.ArgumentParser(description='Clever -- a program for calculation 3D molecular fields')
actions_parsers = parser.add_subparsers(title="Actions",
                                       description="actions available")

set_createdb_parser(actions_parsers)
set_geometry_parser(actions_parsers)
set_charges_parser(actions_parsers)
set_rism_parser(actions_parsers)

args = parser.parse_args()
functions[args.action](**vars(args))

