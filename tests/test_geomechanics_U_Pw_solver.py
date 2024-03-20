import KratosMultiphysics as Kratos
from KratosMultiphysics.StemApplication.geomechanics_U_Pw_solver import UPwUvecSolver


def test_KeepAdvancingSolutionLoop():
    """
    Test the KeepAdvancingSolutionLoop function. Tests if the function stops the solver if the time is reached, while
    taking into account the machine precision.
    """

    model = Kratos.Model()
    settings = Kratos.Parameters("""{}""")
    uvec_solver = UPwUvecSolver(model, settings)

    # check if the function returns True if the time is not reached with a tolerance of the machine precision

    # normal case
    uvec_solver.main_model_part.ProcessInfo.SetValue(Kratos.TIME, 0.1)
    assert uvec_solver.KeepAdvancingSolutionLoop(0.3)

    # time is within machine precision of end time (positive), 0.1+0.2 = 0.30000000000000004, solver should not advance
    uvec_solver.main_model_part.ProcessInfo.SetValue(Kratos.TIME, 0.1 + 0.2)
    assert not uvec_solver.KeepAdvancingSolutionLoop(0.3)

    # time is within machine precision of end time (negative), solver should not advance
    uvec_solver.main_model_part.ProcessInfo.SetValue(Kratos.TIME, 0.3)
    assert not uvec_solver.KeepAdvancingSolutionLoop(0.1 + 0.2)

def test_PrepareModelPart():
    """
    Test the PrepareModelPart function. Tests if the function maintains the current step between stages.
    """

    # initialize model
    model = Kratos.Model()
    settings = Kratos.Parameters("""{}""")

    # get default settings
    default_settings = UPwUvecSolver(model, settings).GetDefaultParameters()

    # refer to empty soil model part
    default_settings["problem_domain_sub_model_part_list"].SetStringArray(["Soil_drained-auto-1"])
    default_settings["processes_sub_model_part_list"].SetStringArray(["Soil_drained-auto-1"])
    default_settings["body_domain_sub_model_part_list"].SetStringArray(["Soil_drained-auto-1"])

    # add material parameters
    default_settings["material_import_settings"]["materials_filename"].SetString(
        "tests/test_data/input_data_multi_stage_uvec/MaterialParameters.json")

    # initialize solver
    uvec_solver = UPwUvecSolver(model, default_settings)

    # add empty sub model part
    uvec_solver.main_model_part.CreateSubModelPart("Soil_drained-auto-1")

    # set current step
    uvec_solver.main_model_part.ProcessInfo.SetValue(Kratos.STEP, 5)

    # call function
    uvec_solver.PrepareModelPart()

    # check if the current step is maintained
    assert uvec_solver.main_model_part.ProcessInfo[Kratos.STEP] == 5
