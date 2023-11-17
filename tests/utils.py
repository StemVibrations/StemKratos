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

        stage.Run()

        # change working directory back to original working directory
        os.chdir(cwd)

        return model, stage