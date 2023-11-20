
from tests.utils import Utils


def test_call_uvec():

    test_file_dir = r"tests/test_data/input_data_expected_moving_load_uvec"

    parameter_file_name = "ProjectParameters_stage1.json"

    model, stage = Utils.run_stage(test_file_dir, parameter_file_name)





if __name__ == '__main__':
    test_call_uvec()