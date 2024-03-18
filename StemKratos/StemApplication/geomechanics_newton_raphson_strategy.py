from KratosMultiphysics.GeoMechanicsApplication import GeoMechanicsNewtonRaphsonStrategy
import KratosMultiphysics.StructuralMechanicsApplication as KSM
from KratosMultiphysics.StemApplication.uvec_controller import StemUvecController

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

    def re_initialize_condition_solution_step(self):
        """
        This function sets the correct value of the load as retrieved from the uvec model, to the Kratos condition.
        """
        precision = 1e-12
        for axle in self.uvec_controller.axle_model_parts:
            for condition in axle.Conditions:
                if not all(abs(dimLoad) < precision for dimLoad in condition.GetValue(KSM.POINT_LOAD)):
                    condition.SetValue(KSM.POINT_LOAD, axle.GetValue(KSM.POINT_LOAD))

    def SolveSolutionStep(self):
        """
        This function executes the solution step of the Stem GeoMechanics NewtonRaphson Strategy.

        this function calls the uvec model each iteration and updates the kratos condition with the result. Furthermore,
        each non-linear iteration, 1 regular newton-raphson iteration is performed, in order to solve the Kratos
        problem.

        """

        print("Info: Stem SolverSolutionStep")

        # update dt in uvec json string
        self.uvec_controller.update_dt(self.uvec_data)

        for iter_no in range(self.max_iters):

            print("Info: Stem Non_Linear Iteration: ", iter_no + 1)

            # update UVEC json string from Kratos
            print("Info: Updating UVEC json string from Kratos")
            self.uvec_controller.update_uvec_from_kratos(self.uvec_data)

            # call UVEC dll and update kratos data
            print("Info: Executing UVEC and updating Kratos with result")            
            self.uvec_data = self.uvec_controller.execute_uvec_update_kratos(self.uvec_data)

            # set correct condition values
            self.re_initialize_condition_solution_step()

            # call Kratos solver
            is_converged = super().SolveSolutionStep()

            # If Kratos has converged, return True
            if is_converged:
                return True

        # If Kratos has not converged, return False
        return False