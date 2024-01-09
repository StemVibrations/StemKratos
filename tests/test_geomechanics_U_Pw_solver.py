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
