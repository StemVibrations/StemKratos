from setuptools import setup
from setuptools.command.install import install
import os
import shutil
import sys
import platform

def set_install_requirements():
    """
    Creates kratos requirements list
    """

    kratos_version = "10.1.0.1"
    python_version_part = ""
    platform_part = ""

    # get platform part of wheel the name
    if (sys.platform == "win32"):
        platform_part = "-win_amd64.whl"
    elif (sys.platform == "linux"):
        platform_part = "-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"

    # get python version part of the wheel name
    if (platform.python_version().startswith("3.10.")):
        python_version_part = '-cp310-cp310'
    elif (platform.python_version().startswith("3.11.")):
        python_version_part = '-cp311-cp311'
    elif (platform.python_version().startswith("3.12.")):
        python_version_part = '-cp312-cp312'

    requirements = [
        f"KratosMultiphysics @ https://github.com/StemVibrations/StemKratos/raw/support_higher_order/StemKratos/wheels/KratosMultiphysics-{kratos_version}{python_version_part}{platform_part}",
        f"KratosLinearSolversApplication @ https://github.com/StemVibrations/StemKratos/raw/support_higher_order/StemKratos/wheels/KratosLinearSolversApplication-{kratos_version}{python_version_part}{platform_part}",
        f"KratosStructuralMechanicsApplication @ https://github.com/StemVibrations/StemKratos/raw/support_higher_order/StemKratos/wheels/KratosStructuralMechanicsApplication-{kratos_version}{python_version_part}{platform_part}",
        f"KratosGeoMechanicsApplication @ https://github.com/StemVibrations/StemKratos/raw/support_higher_order/StemKratos/wheels/KratosGeoMechanicsApplication-{kratos_version}{python_version_part}{platform_part}"
                    ]

    return requirements

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
        source_path = os.path.join(self.install_lib, os.path.join('StemKratos','StemApplication'))
        destination_path = os.path.join(self.install_lib, 'KratosMultiphysics')

        # Ensure the destination directory exists
        os.makedirs(destination_path, exist_ok=True)

        # Move the entire directory
        shutil.move(source_path, destination_path)


if __name__ == '__main__':
    setup(
        install_requires=set_install_requirements(),
        cmdclass={
            'install': CustomStemInstallCommand,
    })
