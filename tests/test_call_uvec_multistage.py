import os
from pathlib import Path
from tests.utils import assert_files_equal, assert_floats_in_files_almost_equal

import KratosMultiphysics as Kratos
import KratosMultiphysics.StemApplication.geomechanics_analysis as analysis


def test_call_uvec_multi_stage():
    """
    Test the call of the UVEC in a multi-stage analysis
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

    # calculated disp below first wheel
    calculated_disp_file = Path(r"tests/test_data/input_data_multi_stage_uvec/output/calculated_disp")
    expected_disp_file = Path(r"tests/test_data/input_data_multi_stage_uvec/_output/expected_disp")

    # check if calculated disp below first wheel is equal to expected disp
    are_files_equal = assert_floats_in_files_almost_equal(calculated_disp_file, expected_disp_file)
    # remove calculated disp file as data is appended
    calculated_disp_file.unlink()
    assert are_files_equal

    expected_vtk_output_dir = Path("tests/test_data/input_data_multi_stage_uvec/_output/all")

    main_vtk_output_dir = Path("tests/test_data/input_data_multi_stage_uvec/output/porous_computational_model_part_1")
    stage_vtk_output_dir = Path("tests/test_data/input_data_multi_stage_uvec/output/porous_computational_model_part_2")

    # move all vtk files in stage vtk output dir to main vtk output dir
    for file in os.listdir(stage_vtk_output_dir):
        if file.endswith(".vtk"):
            os.rename(stage_vtk_output_dir / file, main_vtk_output_dir / file)

    # remove the stage vtk output dir if it is empty
    if not os.listdir(stage_vtk_output_dir):
        os.rmdir(stage_vtk_output_dir)

    # check if vtk files are equal
    assert assert_files_equal(expected_vtk_output_dir, main_vtk_output_dir)



