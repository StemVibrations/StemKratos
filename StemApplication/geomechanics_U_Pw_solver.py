# Import base class file
import KratosMultiphysics
import KratosMultiphysics.GeoMechanicsApplication as GeoMechanicsApplication

from KratosMultiphysics.GeoMechanicsApplication.geomechanics_U_Pw_solver import UPwSolver as GeoSolver
from KratosMultiphysics.StemApplication.geomechanics_newton_raphson_strategy import StemGeoMechanicsNewtonRaphsonStrategy


def CreateSolver(model, custom_settings):
    return UPwSolver(model, custom_settings)


class UPwSolver(GeoSolver):

    def __init__(self, model, custom_settings):
        super().__init__(model, custom_settings)

    @classmethod
    def GetDefaultParameters(cls):
        this_defaults = KratosMultiphysics.Parameters("""{
            "solver_type": "geomechanics_U_Pw_solver",
            "model_part_name": "PorousDomain",
            "domain_size": 2,
            "model_import_settings":{
                "input_type": "mdpa",
                "input_filename": "unknown_name"
            },
            "material_import_settings" :{
                "materials_filename": ""
            },
            "time_stepping": {
                "time_step": 0.1
            },
            "buffer_size": 2,
            "echo_level": 0,
            "rebuild_level": 2,
            "reform_dofs_at_each_step": false,
            "clear_storage": false,
            "compute_reactions": false,
            "move_mesh_flag": false,
            "nodal_smoothing": false,
            "reset_displacements":  false,
            "solution_type": "quasi_static",
            "scheme_type": "Newmark",
            "newmark_beta": 0.25,
            "newmark_gamma": 0.5,
            "newmark_theta": 0.5,
            "rayleigh_m": 0.0,
            "rayleigh_k": 0.0,
            "strategy_type": "newton_raphson",
            "max_piping_iterations": 50,
            "convergence_criterion": "Displacement_criterion",
            "water_pressure_relative_tolerance": 1.0e-4,
            "water_pressure_absolute_tolerance": 1.0e-9,
            "displacement_relative_tolerance": 1.0e-4,
            "displacement_absolute_tolerance": 1.0e-9,
            "residual_relative_tolerance": 1.0e-4,
            "residual_absolute_tolerance": 1.0e-9,
            "desired_iterations"         : 4,
            "max_radius_factor"          : 20.0,
            "min_radius_factor"          : 0.5,
            "max_iterations"             : 15,
            "min_iterations"             : 6,
            "number_cycles"              : 5,
            "increase_factor"            : 2.0,
            "reduction_factor"           : 0.5,
            "calculate_reactions"        : true,
            "max_line_search_iterations" : 5,
            "first_alpha_value"          : 0.5,
            "second_alpha_value"         : 1.0,
            "min_alpha"                  : 0.1,
            "max_alpha"                  : 2.0,
            "line_search_tolerance"      : 0.5,
            "rotation_dofs"              : false,
            "block_builder"              : true,
            "prebuild_dynamics"          : false,
            "search_neighbours_step"     : false,
            "linear_solver_settings":{
                "solver_type": "AMGCL",
                "tolerance": 1.0e-6,
                "max_iteration": 100,
                "scaling": false,
                "verbosity": 0,
                "preconditioner_type": "ILU0Preconditioner",
                "smoother_type": "ilu0",
                "krylov_type": "gmres",
                "coarsening_type": "aggregation"
            },
            "problem_domain_sub_model_part_list": [""],
            "processes_sub_model_part_list": [""],
            "body_domain_sub_model_part_list": [""],
            "loads_sub_model_part_list": [],
            "loads_variable_list": [],
            "uvec"			         :    {
                "uvec_path"              :     "",
                "uvec_method"		     :     "",
                "uvec_model_part"		 :	   "",
                "uvec_data"				 :     {"parameters":{}, "state":{}}
            }
        }""")

        this_defaults.AddMissingParameters(super().GetDefaultParameters())
        return this_defaults


    def _ConstructSolver(self, builder_and_solver, strategy_type):
        self.main_model_part.ProcessInfo.SetValue(GeoMechanicsApplication.IS_CONVERGED, True)
        self.main_model_part.ProcessInfo.SetValue(KratosMultiphysics.NL_ITERATION_NUMBER, 1)

        max_iters = self.settings["max_iterations"].GetInt()
        compute_reactions = self.settings["compute_reactions"].GetBool()
        reform_step_dofs = self.settings["reform_dofs_at_each_step"].GetBool()
        move_mesh_flag = self.settings["move_mesh_flag"].GetBool()
        uvec_data = self.settings["uvec"]

        if strategy_type.lower() == "newton_raphson":
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
        elif strategy_type.lower() == "newton_raphson_with_piping":
            raise RuntimeError(f"Unsupported STEM strategy type '{strategy_type}'")

        elif strategy_type.lower() == "line_search":
            raise RuntimeError(f"Unsupported STEM strategy type '{strategy_type}'")

        elif strategy_type.lower() == "arc_length":
            raise RuntimeError(f"Unsupported STEM strategy type '{strategy_type}'")

        elif strategy_type.lower() == "linear":
            raise RuntimeError(f"Unsupported STEM strategy type '{strategy_type}'")

        else:
            raise RuntimeError(f"Undefined strategy type '{strategy_type}'")

        return solving_strategy
