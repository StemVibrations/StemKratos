from setuptools import setup
from setuptools.command.install import install
import os
import shutil

class CustomStemInstallCommand(install):
    def run(self):
        # Call the default install process
        install.run(self)
        
        # Custom logic to move data from my_package to another_package
        source_path = 'StemKratos/StemApplication'

        # temporary path to store the data
        tmp_path = "StemKratos/tmpPath"
        destination_path = os.path.join(self.install_lib, 'KratosMultiphysics')

        # Ensure the destination directory exists
        os.makedirs(destination_path, exist_ok=True)

        # First copy the directory to a temporary location to prevent permission issues
        # Then move the entire directory
        shutil.copytree(source_path, tmp_path)
        shutil.move(tmp_path, destination_path)

if __name__ == '__main__':
    setup(
    cmdclass={
        'install': CustomStemInstallCommand,
    })
