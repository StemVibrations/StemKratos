# Importing the Kratos Library
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as KSM
from KratosMultiphysics.StemApplication.set_moving_load_process import StemSetMovingLoadProcess

class SetMultipleMovingLoadsProcess(KratosMultiphysics.Process):

    def __init__(self, model_part, settings):
        KratosMultiphysics.Process.__init__(self)
        self.moving_loads = []
        self.model_part = model_part
        self.settings = settings
        self.root_model_part = self.model_part.GetRootModelPart()
        self.compute_model_part = self.root_model_part.GetSubModelPart(self.settings["compute_model_part_name"].GetString())

        count = 1
        for offset in settings["configuration"].values():
            print("Offset Python: ", offset.values()[0])
            print(count)
            moving_load_parameters = KratosMultiphysics.Parameters(settings).Clone()
            new_model_part_name = settings["model_part_name"].GetString().split('.')[-1] + "_cloned_" + str(count)
            new_model_part = self.clone_moving_condition_in_compute_model_part(new_model_part_name)
            moving_load_parameters.AddString("model_part_name", new_model_part_name)
            moving_load_parameters.RemoveValue("configuration")
            moving_load_parameters.RemoveValue("compute_model_part_name")
            moving_load_parameters.AddDouble("offset", float(count))
            self.moving_loads.append(StemSetMovingLoadProcess(new_model_part, moving_load_parameters))
            count += 1
        self.remove_cloned_conditions()
        
    def get_max_conditions_index(self):
        max_index = 0
        for condition in self.model_part.GetRootModelPart().Conditions:
            if condition.Id > max_index:
                max_index = condition.Id
        return max_index

    def clone_moving_condition_in_compute_model_part(self, new_body_part_name):
        new_model_part = self.compute_model_part.CreateSubModelPart(new_body_part_name)
        new_model_part.SetValue(KSM.POINT_LOAD, self.settings["load"].GetVector())
        node_ids = [node.Id for node in self.model_part.GetNodes()]
        new_model_part.AddNodes(node_ids)
        index = self.get_max_conditions_index()
        for condition in self.model_part.Conditions:
            index += 1
            node_ids = [node.Id for node in condition.GetNodes()]
            print("Node ids: ", node_ids)
            new_model_part.CreateNewCondition("MovingLoadCondition2D3N", index, node_ids, condition.Properties)
        return new_model_part

    def remove_cloned_conditions(self):
        for condition in self.model_part.Conditions:
            condition.Set(KratosMultiphysics.TO_ERASE, True)
        self.compute_model_part.RemoveConditions(KratosMultiphysics.TO_ERASE)

    def ExecuteInitialize(self):
        for moving_load in self.moving_loads:
            moving_load.ExecuteInitialize()

    def ExecuteInitializeSolutionStep(self):
        for moving_load in self.moving_loads:
            moving_load.ExecuteInitializeSolutionStep()

    def ExecuteFinalizeSolutionStep(self):
        for moving_load in self.moving_loads:
            moving_load.ExecuteFinalizeSolutionStep()


def Factory(settings, model):
    """
    This process sets multiple moving load conditions. The 'load' is to be filled in in x,y and z direction. The 'direction'
    parameter indicates the direction of the movement of the load in x,y and z direction, this parameter is either a
    positive or a negative integer; note that the load follows a given line, thus the 'direction' parameter is not a
    normalised direction vector. The 'velocity' parameter indicates the velocity of the load in the given direction,
    this parameter can be either a double or a function of time, written as a string. The 'origin' parameter indicates
    the origin point of the moving load, note that this point needs to be located within the line condition. The configuration
    term provides the offset distance offset along the moving load line condition for each moving point load
    """
    if not isinstance(settings, KratosMultiphysics.Parameters):
        raise RuntimeError("Expected input shall be a Parameters object, encapsulating a json string")

    default_settings = KratosMultiphysics.Parameters("""
            {
                "help"                    : "This process applies a moving load condition belonging to a modelpart. The load moves over line elements.",
                "model_part_name"         : "please_specify_model_part_name",
                "compute_model_part_name" : "please_specify_compute_model_part_name",
                "variable_name"           : "POINT_LOAD",
                "load"                    : [0.0, 1.0, 0.0],
                "direction"               : [1,1,1],
                "velocity"                : 1,
                "origin"                  : [0.0,0.0,0.0],
                "configuration"           : [0.0]
            }
            """
                                                     )
    load_settings = settings["Parameters"]
    load_settings.ValidateAndAssignDefaults(default_settings)

    # Set process
    model_part = model.GetModelPart(load_settings["model_part_name"].GetString())
    return SetMultipleMovingLoadsProcess(model_part, load_settings)

