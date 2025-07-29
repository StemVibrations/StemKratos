import KratosMultiphysics as Kratos
from KratosMultiphysics.StemApplication.geomechanics_U_Pw_solver import UPwUvecSolver

import pytest

def test_ConstructSolver_invalid_time_stepping():
    """
    Test the ConstructSolver function. Tests if the function raises an error if the time step is not a multiple of the
    total time.
    """
    # initialize model and settings
    model = Kratos.Model()

    invalid_time_stepping_settings = Kratos.Parameters("""{
            "time_step": 0.3,
            "end_time": 1.0,
            "start_time": 0.0
    }""")

    settings = UPwUvecSolver(model, Kratos.Parameters("""{}""")).GetDefaultParameters()

    settings["time_stepping"] =  invalid_time_stepping_settings

    # test if the function raises an error if the time step is not a multiple of the total time
    uvec_solver = UPwUvecSolver(model, settings)
    with pytest.raises(ValueError,
                       match="The time step is not a multiple of the total time. Please adjust the time step."):
        uvec_solver._create_solving_strategy(None,"newton_raphson_linear_elastic" )

    with pytest.raises(ValueError,
                       match="The time step is not a multiple of the total time. Please adjust the time step."):
        uvec_solver._create_solving_strategy(None,"newton_raphson_linear_elastic_with_uvec" )

def test_ConstructSolver_valid_time_stepping():
    """
    Test the ConstructSolver function. Tests if the function does not raise an error if the time step is a multiple of
    the total time.
    """
    # initialize model and settings
    model = Kratos.Model()

    end_time = 0.02 + 0.4

    # expected floating point error
    assert end_time != 0.42

    valid_time_stepping_settings = Kratos.Parameters(f"""{{
            "time_step": 0.004,
            "end_time": {end_time},
            "start_time": 0.02
    }}""")

    settings = UPwUvecSolver(model, Kratos.Parameters("""{}""")).GetDefaultParameters()

    # set the solver type to an invalid type to cancel the run, the run is cancelled after the time step checking
    settings["solver_type"].SetString("cancel_run")

    settings["time_stepping"] =  valid_time_stepping_settings

    # test if the function does not raise an error if the time step is a multiple of the total time
    uvec_solver = UPwUvecSolver(model, settings)

    # the solver raised an error after the time step checking
    with pytest.raises(ValueError,
                       match="The selected strategy, newton_raphson_linear_elastic_with_uvec, "
                             "is only available for the U-Pw solver, dynamic solution type and newmark scheme"):
        uvec_solver._create_solving_strategy(None,"newton_raphson_linear_elastic_with_uvec" )



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
    Test the PrepareModelPart function. Tests if the function maintains the current step between stages. Also tests if
    the first and second derivative of displacement are set to zero.
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

    default_settings["rotation_dofs"].SetBool(True)
    default_settings["solution_type"].SetString("dynamic")

    # initialize solver
    uvec_solver = UPwUvecSolver(model, default_settings)

    # add empty sub model part
    uvec_solver.main_model_part.CreateSubModelPart("Soil_drained-auto-1")

    # add variables to sub model part
    uvec_solver.AddVariables()
    uvec_solver.main_model_part.CreateNewNode(1, 0.0, 0.0, 0.0)

    # set a value to velocity and acceleration
    uvec_solver.main_model_part.GetNode(1).SetSolutionStepValue(Kratos.VELOCITY, 0, [1,2,3])
    uvec_solver.main_model_part.GetNode(1).SetSolutionStepValue(Kratos.ACCELERATION, 0, [4,5,6])

    uvec_solver.main_model_part.GetNode(1).SetSolutionStepValue(Kratos.ANGULAR_VELOCITY, 0, [1,2,3])
    uvec_solver.main_model_part.GetNode(1).SetSolutionStepValue(Kratos.ANGULAR_ACCELERATION, 0, [4,5,6])

    # set current step
    uvec_solver.main_model_part.ProcessInfo.SetValue(Kratos.STEP, 5)

    # call function
    uvec_solver.PrepareModelPart()

    # check if the first and second derivative of displacement are maintained after PrepareModelPart
    calculated_velocities = [velocity_val for velocity_val in
                             uvec_solver.main_model_part.GetNode(1).GetSolutionStepValue(Kratos.VELOCITY, 0)]

    calculated_accelerations = [acceleration_val for acceleration_val in
                                uvec_solver.main_model_part.GetNode(1).GetSolutionStepValue(Kratos.ACCELERATION, 0)]

    calculated_angular_velocities = [angular_velocity_val for angular_velocity_val in
                                uvec_solver.main_model_part.GetNode(1).GetSolutionStepValue(Kratos.ANGULAR_VELOCITY, 0)]

    calculated_angular_accelerations = [angular_acceleration_val for angular_acceleration_val in
                                uvec_solver.main_model_part.GetNode(1).GetSolutionStepValue(Kratos.ANGULAR_ACCELERATION, 0)]

    assert calculated_velocities == [1.0,2.0,3.0]
    assert calculated_accelerations == [4.0,5.0,6.0]
    assert calculated_angular_velocities == [1.0,2.0,3.0]
    assert calculated_angular_accelerations == [4.0,5.0,6.0]

    # check if the current step is maintained
    assert uvec_solver.main_model_part.ProcessInfo[Kratos.STEP] == 5

    # call function again with solution type quasi-static
    default_settings["solution_type"].SetString("quasi_static")
    uvec_solver.PrepareModelPart()

    # check if the first and second derivative of displacement are set to zero
    calculated_velocities = [velocity_val for velocity_val in
                             uvec_solver.main_model_part.GetNode(1).GetSolutionStepValue(Kratos.VELOCITY, 0)]

    calculated_accelerations = [acceleration_val for acceleration_val in
                                uvec_solver.main_model_part.GetNode(1).GetSolutionStepValue(Kratos.ACCELERATION, 0)]

    calculated_angular_velocities = [angular_velocity_val for angular_velocity_val in
                                uvec_solver.main_model_part.GetNode(1).GetSolutionStepValue(Kratos.ANGULAR_VELOCITY, 0)]

    calculated_angular_accelerations = [angular_acceleration_val for angular_acceleration_val in
                                uvec_solver.main_model_part.GetNode(1).GetSolutionStepValue(Kratos.ANGULAR_ACCELERATION, 0)]

    assert calculated_velocities == [0.0,0.0,0.0]
    assert calculated_accelerations == [0.0,0.0,0.0]
    assert calculated_angular_velocities == [0.0,0.0,0.0]
    assert calculated_angular_accelerations == [0.0,0.0,0.0]
