import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as KSM


class StemSetMovingLoadProcess(KSM.SetMovingLoadProcess):
    """
    This process sets the moving load condition.

    Inheritance:
        - :class:`KratosMultiphysics.StructuralMechanicsApplication.SetMovingLoadProcess`

    Attributes:
        - __do_serialize (bool): bool which indicates if the process is to be serialized
        - __do_clear (bool): bool which indicates if the process is to be cleared at finalize
        - model_part (KratosMultiphysics.ModelPart): model part containing the conditions
        - __serializer (KratosMultiphysics.FileSerializer): serializer for the process
    """

    def __init__(self, model_part: KratosMultiphysics.ModelPart, settings: KratosMultiphysics.Parameters):
        """
        This process sets the moving load condition.

        Args:
            - model_part (KratosMultiphysics.ModelPart): model part containing the conditions
            - settings (KratosMultiphysics.Parameters): settings of the process

        """
        self.__do_serialize = settings["serialize"].GetBool()
        self.__do_clear = settings["clear_at_finalize"].GetBool()

        # remove the serialize and clear_at_finalize parameters from the settings as they are not used in the base class
        settings.RemoveValue("serialize")
        settings.RemoveValue("clear_at_finalize")

        super().__init__(model_part, settings)
        self.model_part = model_part

        # initialize serializer
        if self.__do_serialize:
            self.__serializer = KratosMultiphysics.FileSerializer(
                f"set_moving_load_process_{self.model_part.Name}",
                KratosMultiphysics.SerializerTraceType.SERIALIZER_NO_TRACE)

    def ExecuteInitialize(self):
        """
        This function initializes the process. If the simulation is further than the first step,
        the set_moving_load_process is loaded. This function name cannot be changed. This name is recognised by Kratos.
        """

        super().ExecuteInitialize()
        if self.__do_serialize:
            # load if process is restarted
            if self.model_part.ProcessInfo[KratosMultiphysics.STEP] > 0:
                self.__serializer.Load(f"set_moving_load_process_{self.model_part.Name}", self)

    def ExecuteInitializeSolutionStep(self):
        precision = 1e-12
        super().ExecuteInitializeSolutionStep()
        # for condition in self.model_part.Conditions:
        #     # update the of load to the value of the model part if the load is not zero.
        #     # a zero check is done to find the current location of the moving load
        #     if not all(abs(dimLoad) < precision for dimLoad in condition.GetValue(KSM.POINT_LOAD)):
        #         condition.SetValue(KSM.POINT_LOAD, self.model_part.GetValue(KSM.POINT_LOAD))

    def ExecuteFinalize(self):
        super().ExecuteFinalize()

        if self.__do_serialize:
            # save the moving load process to file
            self.__serializer.Save(f"set_moving_load_process_{self.model_part.Name}", self)

        if self.__do_clear:
            # remove the nodes and conditions from the model part as required for multistage analysis
            for node in self.model_part.Nodes:
                node.Set(KratosMultiphysics.TO_ERASE, True)
            self.model_part.RemoveNodes(KratosMultiphysics.TO_ERASE)

            for condition in self.model_part.Conditions:
                condition.Set(KratosMultiphysics.TO_ERASE, True)
            self.model_part.RemoveConditions(KratosMultiphysics.TO_ERASE)


def Factory(settings, Model):
    """
    This process sets the moving load condition. The 'load' is to be filled in x,y and z direction. The 'direction'
    parameter indicates the direction of the movement of the load in x,y and z direction, this parameter is either a
    positive or a negative integer; note that the load follows a given line, thus the 'direction' parameter is not a
    normalised direction vector. The 'velocity' parameter indicates the velocity of the load in the given direction,
    this parameter can be either a double or a function of time, written as a string. The 'origin' parameter indicates
    the origin point of the moving load, note that this point needs to be located within the line condition.
    """
    if not isinstance(settings, KratosMultiphysics.Parameters):
        raise Exception("expected input shall be a Parameters object, encapsulating a json string")

    default_settings = KratosMultiphysics.Parameters("""
            {
                "help"            : "This process applies a moving load condition belonging to a modelpart. The load moves over line elements.",
                "model_part_name" : "please_specify_model_part_name",
                "variable_name"   : "POINT_LOAD",
                "load"            : [0.0, 0.0, 0.0],
                "direction"       : [1,1,1],
                "velocity"        : 1,
                "origin"          : [0.0,0.0,0.0],
                "offset"          : 0.0,
                "serialize"       : False,
                "clear_at_finalize" : False
            }
            """
                                                     )
    load_settings = settings["Parameters"]
    load_settings.ValidateAndAssignDefaults(default_settings)

    # Set process
    model_part = Model.GetModelPart(load_settings["model_part_name"].GetString())
    return StemSetMovingLoadProcess(model_part, load_settings)