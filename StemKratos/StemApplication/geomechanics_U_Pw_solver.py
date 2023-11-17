# Import base class file
import KratosMultiphysics
import KratosMultiphysics.GeoMechanicsApplication as GeoMechanicsApplication

from KratosMultiphysics.GeoMechanicsApplication.geomechanics_U_Pw_solver import UPwSolver as UPwGeoSolver
from KratosMultiphysics.StemApplication.geomechanics_newton_raphson_strategy import StemGeoMechanicsNewtonRaphsonStrategy


def CreateSolver(model, custom_settings):
    return UPwUvecSolver(model, custom_settings)


class UPwUvecSolver(UPwGeoSolver):

    def __init__(self, model, custom_settings):
        super().__init__(model, custom_settings)

    @classmethod
    def GetDefaultParameters(cls):
        this_defaults = super().GetDefaultParameters()

        this_defaults.AddValue("uvec", KratosMultiphysics.Parameters("""{
            "uvec_path"              :     "",
            "uvec_method"		     :     "",
            "uvec_model_part"		 :	   "",
            "uvec_data"				 :     {"parameters":{}, "state":{}}
            }"""))


        this_defaults.AddMissingParameters(super().GetDefaultParameters())
        return this_defaults

    def _ConstructSolver(self, builder_and_solver, strategy_type):

        if strategy_type.lower() == "newton_raphson_with_uvec":

            self.main_model_part.ProcessInfo.SetValue(GeoMechanicsApplication.IS_CONVERGED, True)
            self.main_model_part.ProcessInfo.SetValue(KratosMultiphysics.NL_ITERATION_NUMBER, 1)

            max_iters = self.settings["max_iterations"].GetInt()
            compute_reactions = self.settings["compute_reactions"].GetBool()
            reform_step_dofs = self.settings["reform_dofs_at_each_step"].GetBool()
            move_mesh_flag = self.settings["move_mesh_flag"].GetBool()
            uvec_data = self.settings["uvec"]

            self.strategy_params = KratosMultiphysics.Parameters("{}")
            self.strategy_params.AddValue("loads_sub_model_part_list", self.loads_sub_sub_model_part_list)
            self.strategy_params.AddValue("loads_variable_list", self.settings["loads_variable_list"])
            solving_strategy = StemGeoMechanicsNewtonRaphsonStrategy(self.computing_model_part,
                                                                     self.scheme,
                                                                     self.linear_solver,
                                                                     self.convergence_criterion,
                                                                     builder_and_solver,
                                                                     self.strategy_params,
                                                                     max_iters,
                                                                     compute_reactions,
                                                                     reform_step_dofs,
                                                                     move_mesh_flag,
                                                                     uvec_data)
            return solving_strategy
        else:
            return super()._ConstructSolver(builder_and_solver, strategy_type)
