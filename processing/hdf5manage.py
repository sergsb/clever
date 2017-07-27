import os
from os.path import dirname, basename, splitext
from os.path import join

def get_prefix(file):
    return splitext(basename(file))[0][-3:]

def lock_file(file, prefix):
    new_name = join(dirname(file), basename(file) + ".{}lock".format(prefix))
    os.rename(file,new_name)
    return new_name

def unlock_file(file):
    new_name = join(dirname(file),splitext(basename(file))[0])
    os.rename(file,new_name)
    return new_name

def set_prefix(file,prefix):
    new_name = join(dirname(file), splitext(basename(file))[0][:-3] + "{}.hdf".format(prefix))
    os.rename(file,new_name)
    return new_name

def set_failed(file,prefix):
    new_name = join(dirname(file), basename(file) + ".{}failed".format(prefix))
    os.rename(file,new_name)
    return new_name
