from typing import Union

from KratosMultiphysics.GeoMechanicsApplication import (GeoMechanicsNewtonRaphsonStrategy,
                                                        GeoMechanicNewtonRaphsonStrategyLinearElasticDynamic)
from KratosMultiphysics.StemApplication.uvec_controller import StemUvecController


class StemGeoMechanicsNewtonRaphsonLinearElasticStrategyUvec(GeoMechanicNewtonRaphsonStrategyLinearElasticDynamic):
    """
    Class containing the STEM Geomechanics NewtonRaphson Strategy with a linear elastic solver. Note that the RHS can
    still behave non-linearly. Each non-linear iteration, the solver calls
    the uvec model. The uvec model is used to update the Kratos model. The Kratos model is then solved
    using the linear elastic NewtonRaphson strategy.
    """
    def __init__(self,
                 model_part,
                 scheme,
                 convergence_criterion,
                 builder_and_solver,
                 max_iters,
                 compute_reactions,
                 move_mesh_flag,
                 uvec_data):
        super().__init__(model_part, scheme,  convergence_criterion, builder_and_solver,
                         0, compute_reactions, move_mesh_flag)
        self.model_part = model_part
        self.max_iters = max_iters
        self.uvec_data = uvec_data["uvec_data"]

        self.uvec_controller = StemUvecController(uvec_data, model_part)


    def Initialize(self):
        """
        This function initializes the Stem GeoMechanics NewtonRaphson Strategy, using a linear elastic solver and UVEC.

        """
        # this is needed because the time step has to be known before initialising
        self.uvec_controller.initialise_solution_step(self.uvec_data)
        super().Initialize()

    def SolveSolutionStep(self) -> bool:
        """
        Solve a time step of the Stem GeoMechanics NewtonRaphson Strategy, using a linear elastic solver and UVEC.

        Returns:
            bool: True if the solution converged, False otherwise
        """

        return solve_uvec_solution_step(self)


class StemGeoMechanicsNewtonRaphsonStrategy(GeoMechanicsNewtonRaphsonStrategy):
    """
    Class containing the STEM Geomechanics NewtonRaphson Strategy. Which performs a non-linear iteration, and calls
    the uvec model each iteration. The uvec model is used to update the Kratos model. The Kratos model is then solved
    using the regular NewtonRaphson strategy.
    """

    def __init__(self,
                 model_part,
                 scheme,
                 linear_solver,
                 convergence_criterion,
                 builder_and_solver,
                 strategy_params,
                 max_iters,
                 compute_reactions,
                 reform_step_dofs,
                 move_mesh_flag,
                 uvec_data):
        super().__init__(model_part, scheme, linear_solver, convergence_criterion, builder_and_solver,
                         strategy_params, 0, compute_reactions, reform_step_dofs, move_mesh_flag)
        self.model_part = model_part
        self.max_iters = max_iters
        self.uvec_data = uvec_data["uvec_data"]
        self.uvec_controller = StemUvecController(uvec_data, model_part)

    def SolveSolutionStep(self) -> bool:
        """
        Solve a time step of the Stem GeoMechanics NewtonRaphson Strategy, using a UVEC.

        Returns:
            bool: True if the solution converged, False otherwise

        """

        return solve_uvec_solution_step(self)

def solve_uvec_solution_step(instance: Union[StemGeoMechanicsNewtonRaphsonLinearElasticStrategyUvec, StemGeoMechanicsNewtonRaphsonStrategy]) -> bool:
    """
    This function executes the solution step of the Stem GeoMechanics NewtonRaphson Strategy.

    this function calls the uvec model each iteration and updates the kratos condition with the result. Furthermore,
    each non-linear iteration, 1 regular newton-raphson iteration is performed, in order to solve the Kratos
    problem.

    Args:
        instance (Union[:class:`StemGeoMechanicsNewtonRaphsonLinearElasticStrategyUvec`,
        :class:`StemGeoMechanicsNewtonRaphsonStrategy`]): The instance of the Stem GeoMechanics NewtonRaphson Strategy.

    Returns:
        bool: True if the solution converged, False otherwise

    """
    print("Info: Stem SolverSolutionStep")

    # update dt in uvec json string
    instance.uvec_controller.initialise_solution_step(instance.uvec_data)

    for iter_no in range(instance.max_iters):

        print("Info: Stem Non_Linear Iteration: ", iter_no + 1)

        # update UVEC json string from Kratos
        print("Info: Updating UVEC json string from Kratos")
        instance.uvec_controller.update_uvec_from_kratos(instance.uvec_data)

        # call UVEC dll and update kratos data
        print("Info: Executing UVEC and updating Kratos with result")
        instance.uvec_data = instance.uvec_controller.execute_uvec_update_kratos(instance.uvec_data)

        # call Kratos solver
        is_converged = super(type(instance), instance).SolveSolutionStep()

        # If Kratos has converged, return True
        if is_converged:
            return True

    # If Kratos has not converged, return False
    return False