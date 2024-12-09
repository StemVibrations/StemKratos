import os
from pathlib import Path
from shutil import rmtree
import pytest

import KratosMultiphysics as Kratos
import KratosMultiphysics.StemApplication.geomechanics_analysis as analysis

from tests.utils import assert_files_equal, assert_floats_in_files_almost_equal, Utils


def test_call_uvec_multi_stage():
    """
    Test the call of the UVEC in a multi-stage analysis
    """
    test_file_dir = r"tests/test_data/input_data_multi_stage_uvec"

    project_parameters = ["ProjectParameters_stage1.json", "ProjectParameters_stage2.json"]

    # run the analysis
    Utils.run_multiple_stages(test_file_dir, project_parameters)

    # calculated disp below first wheel
    calculated_disp_file = Path(r"tests/test_data/input_data_multi_stage_uvec/output/calculated_disp")
    expected_disp_file = Path(r"tests/test_data/input_data_multi_stage_uvec/_output/expected_disp")

    # check if calculated disp below first wheel is equal to expected disp
    are_files_equal, message = assert_floats_in_files_almost_equal(calculated_disp_file, expected_disp_file)

    # remove calculated disp file as data is appended
    calculated_disp_file.unlink()
    assert are_files_equal, message

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
    rmtree(main_vtk_output_dir)
    os.remove("tests/test_data/input_data_multi_stage_uvec/set_moving_load_process_moving_load_cloned_1.rest")
    os.remove("tests/test_data/input_data_multi_stage_uvec/set_moving_load_process_moving_load_cloned_2.rest")



def test_call_uvec_multi_stage_expected_fail():
    """
    Test the call of the UVEC in a multi-stage analysis. This test is expected to fail, as extra DOFS are added in the
    second stage
    """
    test_file_dir = r"tests/test_data/input_data_multi_stage_uvec"

    project_parameters = ["ProjectParameters_stage1.json", "ProjectParameters_stage2.json"]

    cwd = os.getcwd()

    # initialize model
    model = Kratos.Model()

    # read first stage parameters
    os.chdir(test_file_dir)
    with open(project_parameters[0], 'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())

    # remove rotation dofs from first stage
    parameters["solver_settings"]["rotation_dofs"].SetBool(False)

    # create and run first stage
    stage = analysis.StemGeoMechanicsAnalysis(model, parameters)
    stage.Run()

    # read second stage parameters
    with open(project_parameters[1], 'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())

    # make sure rotation dofs are added in second stage
    parameters["solver_settings"]["rotation_dofs"].SetBool(True)

    # create second stage with expected fail
    with pytest.raises(RuntimeError) as excinfo:
        analysis.StemGeoMechanicsAnalysis(model, parameters)

    # check if the error message is as expected
    assert ('Error: Attempting to add the variable "ROTATION" to the model part with name "PorousDomain"'
            in str(excinfo.value))

    # change working directory back to original working directory
    os.chdir(cwd)

    # remove uvec disp file
    calculated_disp_file = Path(r"tests/test_data/input_data_multi_stage_uvec/output/calculated_disp")
    calculated_disp_file.unlink()
    rmtree(os.path.join(test_file_dir, "output/porous_computational_model_part_1"))
    os.remove("tests/test_data/input_data_multi_stage_uvec/set_moving_load_process_moving_load_cloned_1.rest")
    os.remove("tests/test_data/input_data_multi_stage_uvec/set_moving_load_process_moving_load_cloned_2.rest")
