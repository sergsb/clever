import argparse
from glob import glob
from os.path import join, abspath

import sys

import time
from mpi4py import MPI
from enum import Enum, IntEnum
import progressbar
from os.path import isdir

from processing.core import set_geometry_parser, set_charges_parser, set_rism_parser, extensions_dict, merge_dicts, main_entrance_point


class MPIStatus( IntEnum ):
    START = 0
    READY = 1
    DONE  = 2
    EXIT  = 3


comm = MPI.COMM_WORLD
size = comm.size
rank = comm.rank
status = MPI.Status()


def master():
    parser = argparse.ArgumentParser ( description='Clever MPI entrance point' )
    actions_parsers = parser.add_subparsers ( title="Actions",
                                              description="actions avaliable" )

    set_geometry_parser ( actions_parsers )
    set_charges_parser ( actions_parsers )
    set_rism_parser ( actions_parsers )

    args = vars(parser.parse_args ())

    assert isdir ( args['database'] )
    path = join ( args['database'], "*{}.hdf".format ( extensions_dict[args['action']] ) )
    files = list ( map ( lambda file: abspath ( file ), glob ( path ) ) )
    assert len ( files ) > 0
    args = list ( map ( lambda file: merge_dicts ( {'file': file}, args ), files ) )

    task_index = 0
    num_workers = size - 1
    closed_workers = 0
    ready = 0
    bar = progressbar.ProgressBar(max_value=len ( args ))

    while closed_workers < num_workers:
        bar.update (ready)
        comm.recv ( source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status )
        source = status.Get_source ( )
        tag = status.Get_tag ( )
        if tag == MPIStatus.READY:
            if task_index < len ( args ):
                comm.send ( args[task_index], dest=source, tag=MPIStatus.START )
                #print ( "Sending task %d to worker %d" % (task_index, source) )
                task_index += 1
            else:
                comm.send ( None, dest=source, tag=MPIStatus.EXIT )
        elif tag == MPIStatus.DONE:
            ready += 1
        elif tag == MPIStatus.EXIT:
            closed_workers += 1
        time.sleep(0.5)


def worker():
    while True:
        comm.send ( None, dest=0, tag=MPIStatus.READY )
        task = comm.recv ( source=0, tag=MPI.ANY_TAG, status=status )
        tag = status.Get_tag ( )
        if tag == MPIStatus.START:
            main_entrance_point(task)
            comm.send (None, dest=0, tag=MPIStatus.DONE )
        elif tag == MPIStatus.EXIT:
            break

if rank == 0:
    master()
else:
    worker()