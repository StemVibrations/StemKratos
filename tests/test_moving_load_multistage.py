import os
from pathlib import Path

from tests.utils import assert_files_equal, Utils


def test_call_moving_load_multi_stage():
    """
    Test the call of a regular moving  in a multi-stage analysis
    """
    test_file_dir = r"tests/test_data/input_data_multi_stage_moving_load"

    project_parameters = ["ProjectParameters_stage_1.json", "ProjectParameters_stage_2.json"]

    # run the analysis
    Utils.run_multiple_stages(test_file_dir, project_parameters)

    expected_vtk_output_dir = Path("tests/test_data/input_data_multi_stage_moving_load/_output/all")

    main_vtk_output_dir = (
        Path("tests/test_data/input_data_multi_stage_moving_load/output/output_vtk_full_model_stage_1"))
    stage_vtk_output_dir = (
        Path("tests/test_data/input_data_multi_stage_moving_load/output/output_vtk_full_model_stage_2"))

    # move all vtk files in stage vtk output dir to main vtk output dir
    for file in os.listdir(stage_vtk_output_dir):
        if file.endswith(".vtk"):
            os.rename(stage_vtk_output_dir / file, main_vtk_output_dir / file)

    # remove the stage vtk output dir if it is empty
    if not os.listdir(stage_vtk_output_dir):
        os.rmdir(stage_vtk_output_dir)

    # check if vtk files are equal
    assert assert_files_equal(expected_vtk_output_dir, main_vtk_output_dir)