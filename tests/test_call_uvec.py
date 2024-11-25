import os
import shutil

from tests.utils import Utils, assert_files_equal


def test_call_uvec():
    """
    Test the call of UVEC against benchmark
    """
    test_file_dir = r"tests/test_data/input_data_expected_moving_load_uvec"

    parameter_file_name = "ProjectParameters_stage1.json"

    Utils.run_multiple_stages(test_file_dir, [parameter_file_name])

    assert assert_files_equal(os.path.join(test_file_dir, "_output/porous_computational_model_part"),
                              os.path.join(test_file_dir, "output/porous_computational_model_part"))

    shutil.rmtree(os.path.join(test_file_dir, "output"))
    os.remove(os.path.join(test_file_dir, "set_moving_load_process_moving_load_cloned_1.rest"))
    os.remove(os.path.join(test_file_dir, "set_moving_load_process_moving_load_cloned_2.rest"))
