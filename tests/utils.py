import os
from typing import Union
from pathlib import Path

import KratosMultiphysics as Kratos
import KratosMultiphysics.StemApplication.geomechanics_analysis as analysis


class Utils():
    @staticmethod
    def run_stage(project_path, project_parameters_file_name="ProjectParameters.json"):
        """
        Runs a single stage of the calculation.

        Args:
            - project_path (str): The path to the project folder.
            - project_parameters_file_name (str): The name of the project parameters file.

        """

        # set stage parameters
        cwd = os.getcwd()
        os.chdir(project_path)

        with open(project_parameters_file_name, 'r') as parameter_file:
            parameters = Kratos.Parameters(parameter_file.read())

        model = Kratos.Model()
        stage = analysis.StemGeoMechanicsAnalysis(model, parameters)

        stage.Run()

        # change working directory back to original working directory
        os.chdir(cwd)

        return model, stage


def assert_files_equal(exact_folder: Union[str, Path], test_folder: Union[str,Path]) -> bool:
    r"""
    Compares two folders containing files and returns True if all files are equal, False otherwise.

    Args:
        - exact_folder (str): The folder containing the exact files.
        - test_folder (str): The folder containing the test files.

    Returns:
        - bool: True if all files are equal, False otherwise.
    """

    # reads all files in directory
    files = os.listdir(exact_folder)

    if len(files) == 0:
        return False
    # checks if all files in exact_folder are in test_folder
    for file in files:
        with open(os.path.join(exact_folder, file)) as fi:
            exact = fi.read()
        with open(os.path.join(test_folder, file)) as fi:
            test = fi.read()

        # check if files are equal
        if exact != test:
            return False
    return True


def assert_floats_in_files_almost_equal(exact_file: Union[str, Path],
                                        test_file: Union[str, Path], decimal: int = 7) -> bool:
    r"""
    Compares two files containing floats and returns True if all floats are equal, False otherwise.

    Args:
        - exact_file (str): The file containing the exact floats.
        - test_file (str): The file containing the test floats.
        - decimal (int): The number of decimal places to compare.

    Returns:
        - bool: True if all floats are equal, False otherwise.
    """

    with open(exact_file, "r") as f:
        exact_data = f.read().splitlines()
    exact_data = [list(map(float, t.split(";"))) for t in exact_data]

    with open(test_file, "r") as f:
        test_data = f.read().splitlines()
    test_data = [list(map(float, t.split(";"))) for t in test_data]

    # check if files are equal
    for exact, test in zip(exact_data, test_data):
        for e, t in zip(exact, test):
            if round(e, decimal) != round(t, decimal):
                return False
    return True