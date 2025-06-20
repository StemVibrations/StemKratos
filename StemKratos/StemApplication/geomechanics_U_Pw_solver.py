import sys

import math
from decimal import Decimal, getcontext

# Import base class file
import KratosMultiphysics
import KratosMultiphysics.GeoMechanicsApplication as GeoMechanicsApplication

from KratosMultiphysics.GeoMechanicsApplication.geomechanics_U_Pw_solver import UPwSolver as UPwGeoSolver
from KratosMultiphysics.StemApplication.geomechanics_newton_raphson_strategy import (StemGeoMechanicsNewtonRaphsonStrategy,
                                                                                     StemGeoMechanicsNewtonRaphsonLinearElasticStrategyUvec)


def CreateSolver(model: KratosMultiphysics.Model, custom_settings: KratosMultiphysics.Parameters)-> 'UPwUvecSolver':
    """
    This function creates the solver according to the solver settings.

    Args:
        - model (Kratos.Model): The Kratos model.
        - custom_settings (Kratos.Parameters): The custom settings of the solver.

    Returns:
        - UPwUvecSolver: The created solver.
    """
    return UPwUvecSolver(model, custom_settings)


class UPwUvecSolver(UPwGeoSolver):

    def __init__(self, model, custom_settings):
        super().__init__(model, custom_settings)

    @classmethod
    def GetDefaultParameters(cls):
        """
        This function returns the default input parameters of the solver.
        """

        # Set default solver parameters from UPw geo solver
        this_defaults = super().GetDefaultParameters()

        # Add uvec parameters
        this_defaults.AddValue("uvec", KratosMultiphysics.Parameters("""{
            "uvec_path"              :     "",
            "uvec_method"		     :     "",
            "uvec_model_part"		 :	   "",
            "uvec_data"				 :     {"parameters":{}, "state":{}}
            }"""))

        # add default time stepping parameters
        this_defaults.AddValue("time_stepping", KratosMultiphysics.Parameters("""{
            "time_step"     : 0.0,
            "start_time"    : 0.0,
            "end_time"      : 0.0
        }"""))

        # add missing parameters
        this_defaults.AddMissingParameters(super().GetDefaultParameters())

        return this_defaults

    def PrepareModelPart(self):
        """
        This function makes sure that the current STEP of the simulation is maintained between stages
        """

        # get current step
        current_step = self.main_model_part.ProcessInfo[KratosMultiphysics.STEP]

        # call base class function
        super().PrepareModelPart()

        # set current step
        self.main_model_part.ProcessInfo.SetValue(KratosMultiphysics.STEP, current_step)

        # set first and second derivative of displacement to zero for all nodes in case of quasi-static analysis
        if self.settings["solution_type"].GetString().lower() == "quasi_static":
            self.__reset_derivatives_to_zero()


    def __reset_derivatives_to_zero(self):
        """
        This function sets the first and second derivative of the displacement and rotation to zero for all nodes in
        the model.
        """
        KratosMultiphysics.VariableUtils().SetHistoricalVariableToZero(KratosMultiphysics.VELOCITY, self.main_model_part.Nodes)
        KratosMultiphysics.VariableUtils().SetHistoricalVariableToZero(KratosMultiphysics.ACCELERATION, self.main_model_part.Nodes)

        if self.settings["rotation_dofs"].GetBool():
            KratosMultiphysics.VariableUtils().SetHistoricalVariableToZero(KratosMultiphysics.ANGULAR_VELOCITY, self.main_model_part.Nodes)
            KratosMultiphysics.VariableUtils().SetHistoricalVariableToZero(KratosMultiphysics.ANGULAR_ACCELERATION, self.main_model_part.Nodes)


    def _create_solving_strategy(self, builder_and_solver: KratosMultiphysics.BuilderAndSolver, strategy_type: str):
        """
        This function constructs the solver according to the solver settings. If newton_raphson_with_uvec is selected,
        the solver is constructed from the StemGeoMechanicsNewtonRaphsonStrategy class. Else the solver is constructed
        from the base class.

        Args:
            - builder_and_solver (KratosMultiphysics.BuilderAndSolver): The builder and solver object.
            - strategy_type (str): The strategy type of the solver.

        return
            - KratosMultiphysics.BaseSolvingStrategy: The constructed solver.
        """

        # check if the time step is a multiple of the total time, Note that this should be moved to the base class
        if (strategy_type.lower() == "newton_raphson_linear_elastic_with_uvec"
                or strategy_type.lower() == "newton_raphson_linear_elastic"):

            time_step = self.settings["time_stepping"]["time_step"].GetDouble()
            end_time = self.settings["time_stepping"]["end_time"].GetDouble()
            start_time = self.settings["time_stepping"]["start_time"].GetDouble()

            # use decimal to avoid floating point errors
            getcontext().prec = 16
            if (Decimal(str(end_time)) - Decimal(str(start_time))) % Decimal(str(time_step)) != Decimal("0.0"):
                raise ValueError("The time step is not a multiple of the total time. Please adjust the time step.")

        # define newton raphson with uvec strategy
        if strategy_type.lower() == "newton_raphson_with_uvec":

            self.main_model_part.ProcessInfo.SetValue(GeoMechanicsApplication.IS_CONVERGED, True)
            self.main_model_part.ProcessInfo.SetValue(KratosMultiphysics.NL_ITERATION_NUMBER, 0)

            max_iters = self.settings["max_iterations"].GetInt()
            compute_reactions = self.settings["compute_reactions"].GetBool()
            reform_step_dofs = self.settings["reform_dofs_at_each_step"].GetBool()
            move_mesh_flag = self.settings["move_mesh_flag"].GetBool()
            uvec_data = self.settings["uvec"]

            self.strategy_params = KratosMultiphysics.Parameters("{}")
            solving_strategy = StemGeoMechanicsNewtonRaphsonStrategy(self.computing_model_part,
                                                                     self.scheme,
                                                                     self.convergence_criterion,
                                                                     builder_and_solver,
                                                                     self.strategy_params,
                                                                     max_iters,
                                                                     compute_reactions,
                                                                     reform_step_dofs,
                                                                     move_mesh_flag,
                                                                     uvec_data)
            return solving_strategy

        elif strategy_type.lower() == "newton_raphson_linear_elastic_with_uvec":

            self.main_model_part.ProcessInfo.SetValue(GeoMechanicsApplication.IS_CONVERGED, True)
            self.main_model_part.ProcessInfo.SetValue(KratosMultiphysics.NL_ITERATION_NUMBER, 0)

            max_iters = self.settings["max_iterations"].GetInt()
            compute_reactions = self.settings["compute_reactions"].GetBool()
            move_mesh_flag = self.settings["move_mesh_flag"].GetBool()
            uvec_data = self.settings["uvec"]

            # check if the solver_type, solution_type and scheme_type are set to the correct values
            if ((self.settings["solver_type"].GetString().lower() != "u_pw")
                    or (self.settings["solution_type"].GetString().lower() != "dynamic")
                    or (self.settings["scheme_type"].GetString().lower() != "newmark")):
                raise ValueError(f"The selected strategy, {strategy_type.lower()}, is only available for the "
                                 f"U-Pw solver, dynamic solution type and newmark scheme")

            # check if the reduction_factor and increase_factor are set to 1.0
            if (not math.isclose(self.settings["reduction_factor"].GetDouble(), 1.0)
                    or not math.isclose(self.settings["increase_factor"].GetDouble(), 1.0)):
                raise ValueError(f"The selected strategy, {strategy_type.lower()}, requires a reduction_factor and "
                                 f"an increase_factor of 1.0.")

            self.strategy_params = KratosMultiphysics.Parameters("{}")

            beta = self.settings["newmark_beta"].GetDouble()
            gamma = self.settings["newmark_gamma"].GetDouble()
            calculate_initial_acceleration = self.settings["initialize_acceleration"].GetBool()

            # delta time has to be initialized before solving solution steps
            self.main_model_part.ProcessInfo[KratosMultiphysics.DELTA_TIME] = self.settings["time_stepping"][
                "time_step"].GetDouble()

            new_scheme = GeoMechanicsApplication.IncrementalNewmarkLinearElasticUScheme(beta, gamma)

            new_builder_and_solver = GeoMechanicsApplication.ResidualBasedBlockBuilderAndSolverLinearElasticDynamic(
                self.linear_solver,
                beta,
                gamma,
                calculate_initial_acceleration)

            solving_strategy = StemGeoMechanicsNewtonRaphsonLinearElasticStrategyUvec(
                self.computing_model_part,
                new_scheme,
                self.convergence_criterion,
                new_builder_and_solver,
                max_iters,
                compute_reactions,
                move_mesh_flag,
                uvec_data)

            return solving_strategy

        else:
            return super()._create_solving_strategy(builder_and_solver, strategy_type)

    def KeepAdvancingSolutionLoop(self, end_time: float) -> bool:
        """
        This function checks if the time step should be continued. The name of the function is kept the same as in the
        base class, such that the function is overwritten. Thus, the name cannot be changed.

        Args:
            - end_time (float): The end time of the simulation.

        Returns:
            - bool: True if the time step should be continued, else False.
        """
        current_time_corrected = self.main_model_part.ProcessInfo[KratosMultiphysics.TIME]
        return current_time_corrected < end_time - sys.float_info.epsilon
