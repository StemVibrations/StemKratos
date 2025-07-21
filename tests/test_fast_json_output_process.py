import json
from pathlib import Path

import numpy.testing as npt
import KratosMultiphysics
from KratosMultiphysics.StemApplication.fast_json_output_process import FastJsonOutputProcess


def test_add_nodal_parameters_process_nodal_concentrated_element():
    """
    This test checks the FastJsonOutputProcess for writing nodal solution step variables to a JSON file.
    """

    # initialize Kratos model
    model = KratosMultiphysics.Model()

    # initialize model part
    json_output_model_part = model.CreateModelPart("json_model_part", 1)
    json_output_model_part.AddNodalSolutionStepVariable(KratosMultiphysics.VELOCITY)
    json_output_model_part.AddNodalSolutionStepVariable(KratosMultiphysics.DISPLACEMENT)

    json_output_model_part.ProcessInfo.SetValue(KratosMultiphysics.TIME, 0.0)
    json_output_model_part.ProcessInfo.SetValue(KratosMultiphysics.DELTA_TIME, 0.1)

    node = json_output_model_part.CreateNewNode(1, 0.0, 0.0, 0.0)
    set_velocity = [1.0, 2.0, 3.0]
    set_displacement = [4.0, 5.0, 6.0]
    node.SetSolutionStepValue(KratosMultiphysics.VELOCITY, set_velocity)
    node.SetSolutionStepValue(KratosMultiphysics.DISPLACEMENT, set_displacement)

    json_output_parameters = KratosMultiphysics.Parameters( """{
            "model_part_name": "json_model_part",
            "output_file_name": "tests/test_data/test_fast_json_output.json",
            "output_variables": [
                "VELOCITY",
                "DISPLACEMENT"
            ],
            "gauss_points_output_variables": [],
            "time_frequency": 1e-5
            }""" )


    # execute the FastJsonOutputProcess
    process = FastJsonOutputProcess(model, json_output_parameters)

    process.ExecuteInitialize()
    process.ExecuteBeforeSolutionLoop()
    process.ExecuteFinalizeSolutionStep()

    # Get the output from the JSON file
    with open("tests/test_data/test_fast_json_output.json", 'r') as f:
        data = json.load(f)

    displacement_node_1 = [data["NODE_1"]["DISPLACEMENT_X"][0], data["NODE_1"]["DISPLACEMENT_Y"][0], data["NODE_1"]["DISPLACEMENT_Z"][0]]
    velocity_node_1 = [data["NODE_1"]["VELOCITY_X"][0], data["NODE_1"]["VELOCITY_Y"][0], data["NODE_1"]["VELOCITY_Z"][0]]


    # Check if the output matches the set values
    npt.assert_array_almost_equal(displacement_node_1, set_displacement)
    npt.assert_array_almost_equal(velocity_node_1, set_velocity)

    # Clean up the output file
    output_file_path = Path("tests/test_data/test_fast_json_output.json")
    if output_file_path.exists():
        output_file_path.unlink()


