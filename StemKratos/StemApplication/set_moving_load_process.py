import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as KSM

class StemSetMovingLoadProcess(KSM.SetMovingLoadProcess):
    """
    This process sets the moving load condition.

    Inheritance:
        - :class: KratosMultiphysics.StructuralMechanicsApplication.SetMovingLoadProcess

    Attributes:
        - __do_serialize (bool): bool which indicates if the process is to be serialized
        - __do_clear (bool): bool which indicates if the process is to be cleared at finalize
        - __is_externally_managed (bool): bool which indicates if the load is externally managed
        - model_part (KratosMultiphysics.ModelPart): model part containing the conditions
        - __serialize_file_name (str): name of the file to serialize the process
        - __serializer_type (KratosMultiphysics.SerializerTraceType): type of the serializer
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
        self.__is_externally_managed = settings["is_externally_managed"].GetBool()

        # remove the serialize and clear_at_finalize parameters from the settings as they are not used in the base class
        settings.RemoveValue("serialize")
        settings.RemoveValue("clear_at_finalize")
        settings.RemoveValue("is_externally_managed")

        super().__init__(model_part, settings)
        self.model_part = model_part

        # initialize serializer variables
        if self.__do_serialize:
            self.__serialize_file_name = f"set_moving_load_process_{self.model_part.Name}"
            self.__serializer_type = KratosMultiphysics.SerializerTraceType.SERIALIZER_NO_TRACE


    def ExecuteInitialize(self):
        """
        This function initializes the process. If the simulation is further than the first step,
        the set_moving_load_process is loaded. This function name cannot be changed as this name is recognised by
        Kratos.
        """

        # load if process is restarted
        if self.__do_serialize and self.model_part.ProcessInfo[KratosMultiphysics.STEP] > 0:

            # create a serializer to load the process and load the process from file
            load_serializer = KratosMultiphysics.FileSerializer(
                self.__serialize_file_name, self.__serializer_type)
            load_serializer.Load(f"set_moving_load_process_{self.model_part.Name}", self)

            is_restarted = self.model_part.ProcessInfo[KratosMultiphysics.IS_RESTARTED]
            self.model_part.ProcessInfo[KratosMultiphysics.IS_RESTARTED] = True

            super().ExecuteInitialize()
            self.model_part.ProcessInfo[KratosMultiphysics.IS_RESTARTED] = is_restarted

        else:
            super().ExecuteInitialize()

    def ExecuteInitializeSolutionStep(self):
        """
        This function initializes the solution step. It updates the load of the conditions to the value of the
        model part if the load is not zero. This function name cannot be changed. This name is recognised by Kratos.

        """

        super().ExecuteInitializeSolutionStep()

        # update the load of the conditions from the value stored in the modelpart only if the value is externally
        # managed
        if self.__is_externally_managed:
            precision = 1e-12
            for condition in self.model_part.Conditions:
                # update the of load to the value of the model part if the load is not zero.
                # a zero check is done to find the current location of the moving load
                if not all(abs(load_magnitude) < precision for load_magnitude in condition.GetValue(KSM.POINT_LOAD)):
                    condition.SetValue(KSM.POINT_LOAD, self.model_part.GetValue(KSM.POINT_LOAD))

    def ExecuteFinalize(self):
        """
        This function finalizes the process. If the serialize parameter is set, the process is saved to file. If the
        clear_at_finalize parameter is set, all data is removed from the model part. This function name
        cannot be changed as this name is recognised by Kratos.
        """
        super().ExecuteFinalize()

        if self.__do_serialize:

            # create a serializer to save the process to file
            save_serializer = KratosMultiphysics.FileSerializer(
                self.__serialize_file_name, self.__serializer_type)

            # save the moving load process to file
            save_serializer.Save(f"set_moving_load_process_{self.model_part.Name}", self)

        if self.__do_clear:
            self.model_part.Clear()


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
                "serialize"       : false,
                "clear_at_finalize" : false,
                "is_externally_managed" : false
            }
            """
                                                     )
    load_settings = settings["Parameters"]
    load_settings.ValidateAndAssignDefaults(default_settings)

    # Set process
    model_part = Model.GetModelPart(load_settings["model_part_name"].GetString())
    return StemSetMovingLoadProcess(model_part, load_settings)