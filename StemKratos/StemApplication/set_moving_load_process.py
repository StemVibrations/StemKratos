import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as KSM

class StemSetMovingLoadProcess(KSM.SetMovingLoadProcess):

    def __init__(self, model_part, settings):
        super().__init__(model_part, settings)
        self.model_part = model_part
        self.serializer = KratosMultiphysics.FileSerializer(f"set_moving_load_process_{self.model_part.Name}",
                                                            KratosMultiphysics.SerializerTraceType.SERIALIZER_NO_TRACE)

    #
    def ExecuteInitialize(self):
        super().ExecuteInitialize()
    #
    #
        tmp1 = self.model_part.ProcessInfo.GetValue(KratosMultiphysics.TIME)
        if tmp1 > 0:
            process = self.serializer.Load(f"set_moving_load_process_{self.model_part.Name}", self)
    #     # process = self.serializer.Load(f"set_moving_load_process_{self.model_part.Name}", self)

    def ExecuteInitializeSolutionStep(self):
        precision = 1e-12
        super().ExecuteInitializeSolutionStep()
        # a = self.model_part.GetRootModelPart().GetSubModelPart(self.settings["compute_model_part_name"].GetString()).ProcessInfo[KratosMultiphysics.IS_RESTARTED]
        # print(self.model_part.ProcessInfo[KratosMultiphysics.IS_RESTARTED])

        # self.root_model_part.GetSubModelPart(self.settings["compute_model_part_name"].GetString())
        # self._GetSolver().GetComputingModelPart().ProcessInfo[KratosMultiphysics.IS_RESTARTED] = True
        # print(simulation._GetSolver().GetComputingModelPart().ProcessInfo[KratosMultiphysics.IS_RESTARTED])

        for condition in self.model_part.Conditions:
            # update the of load to the value of the model part if the load is not zero.
            # a zero check is done to find the current location of the moving load
            if not all(abs(dimLoad) < precision for dimLoad in condition.GetValue(KSM.POINT_LOAD)):
                condition.SetValue(KSM.POINT_LOAD, self.model_part.GetValue(KSM.POINT_LOAD))
                print(f"aron_load{condition.GetValue(KSM.POINT_LOAD)}")
                print(f"aron_position{condition.GetValue(KSM.MOVING_LOAD_LOCAL_DISTANCE)}")

    def ExecuteFinalize(self):
        super().ExecuteFinalize()

        self.serializer.Save(f"set_moving_load_process_{self.model_part.Name}", self)

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
                "offset"          : 0.0
            }
            """
                                                     )
    load_settings = settings["Parameters"]
    load_settings.ValidateAndAssignDefaults(default_settings)

    # Set process
    model_part = Model.GetModelPart(load_settings["model_part_name"].GetString())
    return StemSetMovingLoadProcess(model_part, load_settings)