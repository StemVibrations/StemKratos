# Importing the Kratos Library
import os.path
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as KSM
from KratosMultiphysics.StemApplication.set_moving_load_process import StemSetMovingLoadProcess

# condition name mapper, the key is the dimension and the number of nodes of the condition,
# the value is the name of the condition
CONDITION_NAME_MAP = {(2, 2): "MovingLoadCondition2D2N",
                      (2, 3): "MovingLoadCondition2D3N",
                      (3, 2): "MovingLoadCondition3D2N",
                      (3, 3): "MovingLoadCondition3D3N"}

class SetMultipleMovingLoadsProcess(KratosMultiphysics.Process):

    def __init__(self, model_part, settings):
        KratosMultiphysics.Process.__init__(self)
        self.moving_loads = []
        self.model_part = model_part
        self.settings = settings
        self.root_model_part = self.model_part.GetRootModelPart()
        self.compute_model_part = self.root_model_part.GetSubModelPart(self.settings["compute_model_part_name"].GetString())

        removeConditions = False
        count = 1
        for offset in settings["configuration"].values():
            print("Offset Python: ", offset.values()[0])
            moving_load_parameters = KratosMultiphysics.Parameters(settings).Clone()
            new_model_part_name = settings["model_part_name"].GetString().split('.')[-1] + "_cloned_" + str(count)
            moving_load_parameters.AddString("model_part_name", new_model_part_name)
            moving_load_parameters.RemoveValue("configuration")
            moving_load_parameters.RemoveValue("active")
            moving_load_parameters.RemoveValue("compute_model_part_name")
            
            
            if not self.compute_model_part.HasSubModelPart(new_model_part_name): # check if cloned_model_part_exists
                new_model_part = self.clone_moving_condition_in_compute_model_part(new_model_part_name)
                moving_load_parameters.AddValue("offset", offset.values()[0])
                removeConditions = True
            else:
                new_model_part = self.compute_model_part.GetSubModelPart(new_model_part_name)
                file_name = new_model_part_name + ".tmp"
                if os.path.isfile(file_name):
                    with open(file_name, 'r') as fo:
                        read_offset = float(fo.readline())
                    print("Read Offset", read_offset + offset.GetDouble()) 
                    moving_load_parameters.AddDouble("offset", read_offset)
                else:
                    moving_load_parameters.AddValue("offset", offset.values()[0])
                
            self.moving_loads.append([StemSetMovingLoadProcess(new_model_part, moving_load_parameters), new_model_part_name])
            count += 1

        # remove condition of the original model part, as they are cloned
        self.remove_cloned_conditions()
        
    def get_max_conditions_index(self):
        """
        This function returns the maximum index of the conditions in the main model part
        """
        max_index = 0
        for condition in self.model_part.GetRootModelPart().Conditions:
            if condition.Id > max_index:
                max_index = condition.Id
        return max_index

    def clone_moving_condition_in_compute_model_part(self, new_body_part_name):
        """
        This function clones the moving load condition of the current model part to a new model part
        """
        new_model_part = self.compute_model_part.CreateSubModelPart(new_body_part_name)
        new_model_part.SetValue(KSM.POINT_LOAD, self.settings["load"].GetVector())
        node_ids = [node.Id for node in self.model_part.GetNodes()]
        new_model_part.AddNodes(node_ids)
        index = self.get_max_conditions_index()
        for condition in self.model_part.Conditions:
            index += 1
            node_ids = [node.Id for node in condition.GetNodes()]
            print("Node ids: ", node_ids)
            geom = condition.GetGeometry()
            moving_load_name = CONDITION_NAME_MAP[(geom.WorkingSpaceDimension(), geom.PointsNumber())]

            new_model_part.CreateNewCondition(moving_load_name, index, node_ids, condition.Properties)
        return new_model_part

    def remove_cloned_conditions(self):
        for condition in self.model_part.Conditions:
            condition.Set(KratosMultiphysics.TO_ERASE, True)
        self.compute_model_part.RemoveConditions(KratosMultiphysics.TO_ERASE)

    def ExecuteInitialize(self):
        if self.settings["active"].GetBool():
            print("Execute Initialize")
            for moving_load in self.moving_loads:
                moving_load[0].ExecuteInitialize()

    def ExecuteInitializeSolutionStep(self):
        if self.settings["active"].GetBool():
            print("ExecuteInitializeSolutionStep")
            for moving_load in self.moving_loads:
                moving_load[0].ExecuteInitializeSolutionStep()

    def ExecuteFinalizeSolutionStep(self):
        if self.settings["active"].GetBool():
            print("ExecuteFinalizeSolutionStep")
            for moving_load in self.moving_loads:
                moving_load[0].ExecuteFinalizeSolutionStep()

    def ExecuteFinalize(self):
        if self.settings["active"].GetBool():
            print("ExecuteFinalize")
            for moving_load in self.moving_loads:
                moving_load[0].ExecuteFinalize()
                file_name = moving_load[1] + ".tmp"
                moving_load[0].save(file_name)

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
                "configuration"           : [0.0],
                "active"                  : true
            }
            """
                                                     )
    load_settings = settings["Parameters"]
    load_settings.ValidateAndAssignDefaults(default_settings)

    # Set process
    model_part = model.GetModelPart(load_settings["model_part_name"].GetString())
    return SetMultipleMovingLoadsProcess(model_part, load_settings)

