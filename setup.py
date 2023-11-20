from setuptools import setup
from setuptools.command.install import install
import os
import shutil

class CustomStemInstallCommand(install):
    def run(self):
        r"""
        Install packages STEM Application and KratosMultiphysics
        """
        # Call the default install process
        install.run(self)
        self.run_custom_command()

    def run_custom_command(self):
        """
        Run the custom command to move the package STEMApplication into the KratosMultiphysics
        This needs to be executed after the packages have been installed
        """
        # Custom logic to move data from my_package to another_package
        source_path = os.path.join(self.install_lib, r'StemKratos\StemApplication')
        destination_path = os.path.join(self.install_lib, 'KratosMultiphysics')

        # Ensure the destination directory exists
        os.makedirs(destination_path, exist_ok=True)

        # Move the entire directory
        shutil.move(source_path, destination_path)

if __name__ == '__main__':
    setup(
    cmdclass={
        'install': CustomStemInstallCommand,
    })
