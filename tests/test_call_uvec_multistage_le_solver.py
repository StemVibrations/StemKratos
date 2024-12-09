import os
from pathlib import Path
from shutil import rmtree

from tests.utils import assert_files_equal, assert_floats_in_files_almost_equal, Utils


def test_call_uvec_multi_stage_le_solver():
    """
    Test the call of the UVEC in a multi-stage analysis, using the linear elastic solver.
    """
    test_file_dir = r"tests/test_data/input_data_multi_stage_uvec_le_solver"

    project_parameters = ["ProjectParameters_stage1.json", "ProjectParameters_stage2.json"]

    # run the analysis
    Utils.run_multiple_stages(test_file_dir, project_parameters)

    # calculated disp below first wheel
    calculated_disp_file = Path(r"tests/test_data/input_data_multi_stage_uvec_le_solver/output/calculated_disp")
    expected_disp_file = Path(r"tests/test_data/input_data_multi_stage_uvec_le_solver/_output/expected_disp")

    # check if calculated disp below first wheel is equal to expected disp
    are_files_equal, message = assert_floats_in_files_almost_equal(calculated_disp_file, expected_disp_file)

    # remove calculated disp file as data is appended
    calculated_disp_file.unlink()
    assert are_files_equal, message

    expected_vtk_output_dir = Path("tests/test_data/input_data_multi_stage_uvec_le_solver/_output/all")

    main_vtk_output_dir = Path("tests/test_data/input_data_multi_stage_uvec_le_solver/output/porous_computational_model_part_1")
    stage_vtk_output_dir = Path("tests/test_data/input_data_multi_stage_uvec_le_solver/output/porous_computational_model_part_2")

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
    os.remove("tests/test_data/input_data_multi_stage_uvec_le_solver/set_moving_load_process_moving_load_cloned_1.rest")
    os.remove("tests/test_data/input_data_multi_stage_uvec_le_solver/set_moving_load_process_moving_load_cloned_2.rest")
