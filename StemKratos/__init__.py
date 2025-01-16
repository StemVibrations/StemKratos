from .__version__ import __version__, __title__

import sys
import os
import json
import shutil
import platform
import site
import subprocess
import importlib.metadata
import sysconfig

from setuptools import setup
from setuptools.command.install import install

def check_package_version(package_name: str, target_version: str) -> bool:
    """
    Check if a package is installed and if the installed version matches the target version

    Args:
        - package_name (str): Name of the package to check
        - target_version (str): Version of the package to check

    Returns:
        bool: True if the package is installed and the version matches the target version, False otherwise
    """
    try:
        # Use `require` to check if the package is installed and get its version
        package_version = importlib.metadata.version(package_name)

        # Compare the installed version with the target version
        return package_version == target_version
    except importlib.metadata.PackageNotFoundError:
        return False

def set_install_requirements(kratos_version: str, branch_name: str, reinstall: bool = False):
    """
    Creates kratos requirements list

    Args:
        - kratos_version (str): Kratos version to be installed
        - branch_name (str): Branch name of the Kratos repository
        - reinstall (bool): Flag to force the reinstallation of the packages
    """

    python_version_part = ""
    platform_part = ""

    # get platform part of wheel the name
    if (sys.platform == "win32"):
        platform_part = "-win_amd64.whl"
    elif (sys.platform == "linux"):
        platform_part = "-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"

    # get python version part of the wheel name
    if (platform.python_version().startswith("3.9.")):
        python_version_part = '-cp39-cp39'
    elif (platform.python_version().startswith("3.10.")):
        python_version_part = '-cp310-cp310'
    elif (platform.python_version().startswith("3.11.")):
        python_version_part = '-cp311-cp311'

    requirements = []
    if not check_package_version("KratosMultiphysics", kratos_version) or reinstall:
        requirements.append(f"KratosMultiphysics@https://github.com/StemVibrations/StemKratos/raw/{branch_name}/StemKratos/wheels/KratosMultiphysics-{kratos_version}{python_version_part}{platform_part}",
        )
    if not check_package_version("KratosLinearSolversApplication", kratos_version) or reinstall:
        requirements.append(f"KratosLinearSolversApplication@https://github.com/StemVibrations/StemKratos/raw/{branch_name}/StemKratos/wheels/KratosLinearSolversApplication-{kratos_version}{python_version_part}{platform_part}",
        )
    if not check_package_version("KratosStructuralMechanicsApplication", kratos_version) or reinstall:
        requirements.append(f"KratosStructuralMechanicsApplication@https://github.com/StemVibrations/StemKratos/raw/{branch_name}/StemKratos/wheels/KratosStructuralMechanicsApplication-{kratos_version}{python_version_part}{platform_part}",
        )
    if not check_package_version("KratosGeoMechanicsApplication", kratos_version) or reinstall:
        requirements.append(f"KratosGeoMechanicsApplication@https://github.com/StemVibrations/StemKratos/raw/{branch_name}/StemKratos/wheels/KratosGeoMechanicsApplication-{kratos_version}{python_version_part}{platform_part}"
        )

    return requirements

def editable_path(folder_path: str) -> str:
    """
    Collect the package location when installed in editable mode.

    Args:
        - folder_path (str): Path to the system package folder

    Returns:
        - str: Path to the package installed in editable mode

    """
    with open(os.path.join(folder_path, "direct_url.json"), "r") as f:
        data = json.load(f)

    path_package = data["url"].split("file://")[1]

    with open(os.path.join(folder_path, "top_level.txt"), "r") as f:
        packages = f.read().splitlines()

    return os.path.join(path_package, packages[0])

def is_installed_editable(package_name: str) -> bool:
    """
    Checks if the given package is installed in editable mode.
    Returns True if installed in editable mode, otherwise False.

    Args:
        - package_name (str): Name of the package to check.

    Returns:
        - bool: True if installed in editable mode, otherwise False.
    """

    return os.path.isfile(os.path.join(site.getsitepackages()[0], f"__editable__.{package_name}.pth"))


def get_package_path() -> str:
    """
    Gets the path to the current package in the site-packages directory.

    Returns:
        - str: Path to the package.
    """

    package_name = "-".join([__title__, __version__])
    site_packages_path = sysconfig.get_paths()["purelib"]

    if not is_installed_editable(package_name):
        # if installed in regular mode
        package_path = os.path.join(site_packages_path, __name__.split(".")[0])
        return package_path
    else:
        # if installed in editable mode
        dist_info_path = os.path.join(site_packages_path, f"{package_name}.dist-info")
        return editable_path(dist_info_path)


def move_stem_application():
    """
    Run the custom command to move the package STEMApplication into the KratosMultiphysics
    This needs to be executed after the packages have been installed
    """
    # Custom logic to move data from my_package to another_package

    source_path = os.path.join(get_package_path(),'StemApplication')

    destination_path = os.path.join(sysconfig.get_paths()["purelib"], 'KratosMultiphysics')

    # Ensure the destination directory exists
    os.makedirs(destination_path, exist_ok=True)

    # Move the entire directory
    shutil.move(source_path, destination_path)



REINSTALL = False

kratos_version = "9.5.0.6"
branch_name = "v1.2"
requirements = set_install_requirements(kratos_version, branch_name, REINSTALL)


# only install the requirements if there are any new ones
if len(requirements) > 0 or REINSTALL:

    for requirement in requirements:
        print(f"Installing {requirement}")
        subprocess.run(['pip', 'install', requirement])

    move_stem_application()

