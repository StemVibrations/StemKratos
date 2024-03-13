import os
from pathlib import Path
import shutil
from tests.utils import Utils, assert_files_equal

import KratosMultiphysics as Kratos
from StemKratos.StemApplication.run_multiple_stages import run_stages
import KratosMultiphysics.StemApplication.geomechanics_analysis as analysis


def test_call_uvec_multi_stage2():
    """
    Test the call of UVEC against benchmark
    """
    test_file_dir = r"tests/test_data/input_data_multi_stage_uvec"

    project_parameters = ["ProjectParameters_stage1.json", "ProjectParameters_stage2.json"]

    cwd = os.getcwd()

    # initialize model
    model = Kratos.Model()

    # loop over all stages
    for file_name in project_parameters:

        # change working directory to test file directory
        os.chdir(test_file_dir)

        # read parameters
        with open(file_name, 'r') as parameter_file:
            parameters = Kratos.Parameters(parameter_file.read())

        # run stage
        stage = analysis.StemGeoMechanicsAnalysis(model, parameters)
        stage.Run()

        # change working directory back to original working directory
        os.chdir(cwd)

    main_vtk_output_dir = Path("tests/test_data/input_data_multi_stage_uvec/output/porous_computational_model_part_1")
    stage_vtk_output_dir = Path("tests/test_data/input_data_multi_stage_uvec/output/porous_computational_model_part_2")

    # move all vtk files in stage vtk output dir to main vtk output dir
    for file in os.listdir(stage_vtk_output_dir):
        if file.endswith(".vtk"):
            os.rename(stage_vtk_output_dir / file, main_vtk_output_dir / file)

    # remove the stage vtk output dir if it is empty
    if not os.listdir(stage_vtk_output_dir):
        os.rmdir(stage_vtk_output_dir)


