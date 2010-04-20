#!/usr/bin/env python
import os, sys
from distutils.core import setup, Command

def get_relative_path():      
    return os.path.dirname(os.path.abspath(os.path.join(os.getcwd(), sys.argv[0])))

class EnvCommand(Command):
    description = "Configure the PYTHONPATH, DATABASE and PATH variables to" +\
    "some sensible defaults, if not already set. Call with -q when eval-ing," +\
    """ e.g.:
        eval `python setup.py -q env`
    """
    
    user_options = [ ]
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass
    
    def run(self):
        shell = os.getenv('SHELL', False).split('/')[-1]
        if not shell == 'bash':
            print 'WARNING: this script expects bash or a derivative'
            print '(you have %s) and uses export to set the environment' % shell
            print 'this may not work for you - YMMV, user beware!.'
        if not os.getenv('COUCHURL', False):
            # Use the default localhost URL if none is configured. 
             print 'export COUCHURL=localhost:5984'
        here = get_relative_path()
        
        tests = here + '/test/python'
        source = here + '/src/python'
        # TODO: Set up a bin path with a shell script wrapper of CLI
        exepth = [source + '/DQIS/']
        pypath=os.getenv('PYTHONPATH', '').strip(':').split(':')
         
        for pth in [tests, source]:
            if pth not in pypath:
                pypath.append(pth)
        
        # We might want to add other executables to PATH
        expath=os.getenv('PATH', '').split(':')
        for pth in exepth:
            if pth not in expath:
                expath.append(pth)  
        # Print out the export commands - this assumes bash is the shell
        print 'export PATH=%s' % ':'.join(expath)    
        print 'export PYTHONPATH=%s' % ':'.join(pypath)
        

def getPackages(package_dirs = []):
    packages = []
    for dir in package_dirs:
        for dirpath, dirnames, filenames in os.walk('./%s' % dir):
            # Exclude things here
            if dirpath not in ['./src/python/', './src/python/IMProv']: 
                pathelements = dirpath.split('/')
                if not 'CVS' in pathelements:
                    path = pathelements[3:]
                    packages.append('.'.join(path))
    return packages

package_dir = {'DQIS': 'src/python/DQIS'}

setup (name = 'dqis',
       version = '1.0',
       maintainer_email = 'hn-cms-wmDevelopment@cern.ch',
       cmdclass = {'env': EnvCommand},
                   #'test' : TestCommand },
       package_dir = package_dir,
       packages = getPackages(package_dir.values()),)
