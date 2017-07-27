import sys
from os.path import join, isfile
import re
from glob import glob
import yaml
import os
import platform

def get_global_environment():
     rootdir = ( os.path.dirname ( os.path.realpath ( __file__ ) ) )
     conf_files = glob(join(rootdir,"..","*.yaml"))
     assert len(conf_files) > 0
     if isfile(join(rootdir,"..","{}.yaml".format(platform.node()))):
         env_file = join(rootdir,"..","{}.yaml".format(platform.node()))
     elif isfile(join(rootdir,"..","default.yaml")):
         env_file = join(rootdir,"..","default.yaml")
     else: raise Exception("Can't find config yaml files with environment")
     with open (env_file , 'r' ) as stream:
          return yaml.load ( stream )['environment']



