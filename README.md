# Clever
[![DOI](https://zenodo.org/badge/98550290.svg)](https://zenodo.org/badge/latestdoi/98550290)

A software for 3D molecular fields calculations. 

# Requirements 
* General requirements
  * [python3](https://www.python.org/) (python2.7 support coming soon)
  * [AmberTools 16](http://ambermd.org)
  * [python-rdkit](http://www.rdkit.org)
  * [h5py](http://www.h5py.org) 
  * [pyyaml](http://pyyaml.org)
  * [six](https://pypi.python.org/pypi/six)
  * [numpy](http://www.numpy.org/)
  * [progressbar2](https://pypi.python.org/pypi/progressbar2)
* MPI support 
  * [mpi4py](http://pythonhosted.org/mpi4py/)
* Parallel processing 
  * [pebble](https://pypi.python.org/pypi/Pebble)

# Description 
This program is a framework for calculation 3D molecular descriptors from molecular structures. 

Initially, you have to prepare the database. Clever can read [sdf](https://en.wikipedia.org/wiki/Chemical_table_file) files and saves the results in [HDF5](http://www.h5py.org/) files.

# Database generation
To do it, use `createdb` command

`python3 clever.py createdb --file <path to sdf file> --properties <list of comma separated properties> --output <output directory>`

This script will create a new directory, and place each structure from sdf file to separate hdf file with names: `<database>_<sequential number in sdf file - 1 >_zzz.hdf`
i.e. `LD50_0_zzz.hdf` denontes the file with first structure from original sdf file

# Conformers generation
To do it, use `geometry` command

`python3 clever.py geometry --database <path to database directory> --number_of_conformers <the maximal number of conformers for generation>`

If the calculation succeeds, the files will be renamed from `zzz` prefix to `gzz`, otherwise troubled molecules will be marked as `gfailed`.

We recommend to do all heavy calculations on a cluster with MPI support

`python3 clevermpi.py geometry --database <path to database directory> --number_of_conformers <the maximal number of conformers to generate>`

# Charges calculations

After conformers generation one can calculate charges. 

`python3 clevermpi.py charges --database <path to database directory>`

If the calculation succeeds, the files will be renamed from `gzz` prefix to `gcz`, otherwise troubled molecules will be marked as `cfailed`.

# 3D-RISM calculations
Once you have a database with charges calculated, it is possible to calculate 3D-RISM scalar fileds. 

`python3 clevermpi.py rism --database <path to database directory>  --xvvfile <path to amber file with solute susceptibility function>
`

If the calculation succeeds, the files will be renamed from `gcz` prefix to `gcr`, otherwise troubled molecules will be marked as `rfailed`.







