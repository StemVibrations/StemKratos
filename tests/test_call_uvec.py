
import os
import KratosMultiphysics as Kratos
import KratosMultiphysics.StemApplication as KratosStem
import KratosMultiphysics.StemApplication.geomechanics_analysis as analysis

def test_call_uvec():

    test_file_dir = r"tests/test_data/input_data_expected_moving_load_uvec"
    parameter_file_name = os.path.join(test_file_dir, "ProjectParameters_stage1.json")

    # set stage parameters
    cwd = os.getcwd()
    os.chdir(test_file_dir)

    with open(parameter_file_name, 'r') as parameter_file:
        parameters = Kratos.Parameters(parameter_file.read())

    model = Kratos.Model()
    stage = analysis.StemGeoMechanicsAnalysis(model, parameters)

    stage.Run()

    # change working directory back to original working directory
    os.chdir(cwd)