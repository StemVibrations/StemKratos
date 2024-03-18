from typing import Dict, Any
import json
from pathlib import Path


def pre_operations(uvec_data: Dict[str, Any]):
    """
    Function to perform pre operations before calling the uvec model.

    Args:
        - uvec_data (Dict[str, Any]): input data for the uvec model

    """

    time_index = uvec_data["time_index"]
    state = uvec_data["state"]

    if time_index <= 0:
        state["previous_time"] = 0
        state["previous_time_index"] = time_index

    if time_index > state["previous_time_index"]:
        state["previous_time"] +=  uvec_data["dt"]


def post_operations(uvec_data: Dict[str, Any]):
    """
    Function to perform post operations after calling the uvec model.

    Args:
        - uvec_data (Dict[str, Any]): input data for the uvec model

    """

    # create the output directory if it does not exist
    Path(uvec_data["parameters"]["output_file_name"]).parent.mkdir(parents=True, exist_ok=True)

    # write to file to compare the results
    with open(uvec_data["parameters"]["output_file_name"], 'a+') as f:
        f.write(f"{uvec_data['state']['previous_time']}; {uvec_data['u']['1'][1]}\n")

    uvec_data["state"]["previous_time_index"] = uvec_data["time_index"]


def uvec_test_stage_1(json_string: str) -> str:
    """
    uvec function for stage 1

    Args:
        - json_string (str): json string containing the uvec data

    Returns:
        - str: json string containing the load data

    """
    uvec_data = json.loads(json_string)

    pre_operations(uvec_data)
    uvec_data['loads'] = {1: [0, -30000, 0], 2: [0, -10000, 0]}
    post_operations(uvec_data)

    return json.dumps(uvec_data)


def uvec_test_stage_2(json_string: str) -> str:
    """
    uvec function for stage 2

    Args:
        - json_string (str): json string containing the uvec data

    Returns:
        - str: json string containing the load data

    """

    uvec_data = json.loads(json_string)

    pre_operations(uvec_data)
    uvec_data['loads'] = {1: [0, -30000, 0], 2: [0, -10000, 0]}
    post_operations(uvec_data)

    return json.dumps(uvec_data)