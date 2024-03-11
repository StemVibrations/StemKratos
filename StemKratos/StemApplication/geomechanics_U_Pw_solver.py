import sys
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

        # add missing parameters
        this_defaults.AddMissingParameters(super().GetDefaultParameters())

        return this_defaults

    def PrepareModelPart(self):
        """This function prepares the ModelPart for being used by the PythonSolver
        """
        # Set ProcessInfo variables
        self.main_model_part.ProcessInfo.SetValue(GeoMechanicsApplication.TIME_UNIT_CONVERTER, 1.0)
        self.main_model_part.ProcessInfo.SetValue(GeoMechanicsApplication.NODAL_SMOOTHING,
                                                  self.settings["nodal_smoothing"].GetBool())


        # step = self.main_model_part.ProcessInfo.GetValue(KratosMultiphysics.STEP)
        if not self.main_model_part.ProcessInfo[KratosMultiphysics.IS_RESTARTED]:
            ## Executes the check and prepare model process (Create computing_model_part and set constitutive law)
            self._ExecuteCheckAndPrepare()
            ## Set buffer size
            self._SetBufferSize()

        if not self.model.HasModelPart(self.settings["model_part_name"].GetString()):
            self.model.AddModelPart(self.main_model_part)

    def _ConstructSolver(self, builder_and_solver, strategy_type):
        """
        This function constructs the solver according to the solver settings. If newton_raphson_with_uvec is selected,
        the solver is constructed from the StemGeoMechanicsNewtonRaphsonStrategy class. Else the solver is constructed
        from the base class.
        """

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
