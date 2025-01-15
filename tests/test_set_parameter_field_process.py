
import KratosMultiphysics as Kratos
from KratosMultiphysics.StemApplication.set_parameter_field_process import StemSetParameterFieldProcess

import warnings


def test_GetVariableBasedOnString():
    """
    Test to check if the variable is correctly retrieved from the imported modules
    """

    # dummy variables with YOUNG_MODULUS, which is a variable which is exported to the python module
    settings = Kratos.Parameters("""{
        "model_part_name": "test",
        "variable_name": "YOUNG_MODULUS",
        "dataset": "dummy",
        "func_type": "json_file",
        "function": "dummy",
        "dataset_file_name": "test_file"
    }""")


    # initialize the set parameter field process
    model = Kratos.Model()
    model.CreateModelPart("test")
    process = StemSetParameterFieldProcess(model, settings)

    variable = process.GetVariableBasedOnString()

    assert variable == Kratos.YOUNG_MODULUS

def test_GetVariableBasedOnString_non_existing_variable_in_python():
    """
    Test to check if a warning is raised when a variable is not present in the imported modules
    """

    # dummy variables with DENSITY_SOLID_dummy, which is a variable which is not exported to the python module
    settings = Kratos.Parameters("""{
        "model_part_name": "test",
        "variable_name": "DENSITY_SOLID_dummy",
        "dataset": "dummy",
        "func_type": "json_file",
        "function": "dummy",
        "dataset_file_name": "test_file"
    }""")


    # initialize the set parameter field process
    model = Kratos.Model()
    model.CreateModelPart("test")
    process = StemSetParameterFieldProcess(model, settings)

    # catch the warnings for the test
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Ensure warnings are triggered

        assert process.GetVariableBasedOnString() is None

    # Check that a warning was raised
    assert len(w) == 1
    assert issubclass(w[-1].category, UserWarning)
    assert str(w[-1].message) == "The variable: DENSITY_SOLID_dummy is not present within the imported modules"


