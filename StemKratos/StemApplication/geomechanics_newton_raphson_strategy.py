from KratosMultiphysics.GeoMechanicsApplication import GeoMechanicsNewtonRaphsonStrategy
import KratosMultiphysics.StructuralMechanicsApplication as KSM
from KratosMultiphysics.StemApplication.uvec_controller import StemUvecController

class StemGeoMechanicsNewtonRaphsonStrategy(GeoMechanicsNewtonRaphsonStrategy):

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
                         strategy_params, 1, compute_reactions, reform_step_dofs, move_mesh_flag)
        self.model_part = model_part
        self.max_iters = max_iters
        self.uvec_data = uvec_data["uvec_data"]
        self.uvec_controller = StemUvecController(uvec_data, model_part)

    def re_initialize_condition_solution_step(self):
        for axle in self.uvec_controller.axle_model_parts:
            for condition in axle.Conditions:
                print("Condition*: ", condition.Id)
            print("Point Load*: ", condition.GetValue(KSM.POINT_LOAD))
            if not all(dimLoad==0.0 for dimLoad in condition.GetValue(KSM.POINT_LOAD)):
                condition.SetValue(KSM.POINT_LOAD, self.model_part.ProcessInfo[KSM.POINT_LOAD])
                print("New Point Load*: ", condition.GetValue(KSM.POINT_LOAD))

    def SolveSolutionStep(self):
        print("Python SolverSolutionStep")
        for iter_no in range(self.max_iters):

            print("Python Non_Linear Iteration Loop", iter_no + 1)

            # call UVEC dll and update kratos data
            self.uvec_controller.execute_uvec_update_kratos(self.uvec_data)

            if iter_no != 0 and not is_converged:
                self.re_initialize_condition_solution_step()

            is_converged = super().SolveSolutionStep()

            self.uvec_controller.update_uvec_from_kratos(self.uvec_data)

            print("Kratos Updating UVEC json string......")

            #self.uvec_data = self.uvec_controller.update_uvec_data_from_kratos(self.model_part, self.uvec_data)

            print("Python SolverSolutionStep iter_no", iter_no + 1, "finished")

            if is_converged:
                return True
        return False