import os
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

        test_file_dir = r"tests/test_data/input_data_expected_moving_load_uvec"

        parameter_file_name = "ProjectParameters_stage1.json"

        # set stage parameters
        cwd = os.getcwd()
        os.chdir(project_path)

        with open(project_parameters_file_name, 'r') as parameter_file:
            parameters = Kratos.Parameters(parameter_file.read())

        model = Kratos.Model()


        stage = analysis.StemGeoMechanicsAnalysis(model, parameters)

        model.GetModelPart("PorousDomain").ProcessInfo.SetValue(Kratos.IS_RESTARTED, True)
        tmp = model.GetModelPart("PorousDomain").ProcessInfo.GetValue(Kratos.IS_RESTARTED)

        with open("ProjectParameters_stage2.json", 'r') as parameter_file:
            parameters2 = Kratos.Parameters(parameter_file.read())

        stage2 = analysis.StemGeoMechanicsAnalysis(model, parameters2)

        stage.Run()
        stage2.Run()

        # change working directory back to original working directory
        os.chdir(cwd)

        return model, stage


def assert_files_equal(exact_folder: str, test_folder: str) -> bool:
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

    # checks if all files in exact_folder are in test_folder
    for file in files:
        with open(os.path.join(exact_folder, file)) as fi:
            exact = fi.read()
        with open(os.path.join(test_folder, file)) as fi:
            test = fi.read()

        # check if files are equal
        if exact == test:
            return True
    return False
