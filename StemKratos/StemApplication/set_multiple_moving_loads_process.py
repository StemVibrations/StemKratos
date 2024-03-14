# Importing the Kratos Library
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
    """
    This process sets multiple moving load conditions on a model part. The moving load conditions are cloned from the
    original model part to a new model part. The moving load conditions are then set to the values of the properties
    of the model part.

    Inheritance:
        - :class:`KratosMultiphysics.Process`

    Attributes:
        - moving_loads (list): list of moving load processes
        - model_part (KratosMultiphysics.ModelPart): model part containing the conditions
        - settings (KratosMultiphysics.Parameters): settings of the process
        - root_model_part (KratosMultiphysics.ModelPart): root model part
        - compute_model_part (KratosMultiphysics.ModelPart): compute model part containing the calculation settings

    """

    def __init__(self, model_part: KratosMultiphysics.ModelPart, settings: KratosMultiphysics.Parameters):
        """
        Initialises multiple moving loads

        Args:
            - model_part (KratosMultiphysics.ModelPart): model part containing the conditions
            - settings (KratosMultiphysics.Parameters): settings of the process

        """
        KratosMultiphysics.Process.__init__(self)
        self.moving_loads = []
        self.model_part = model_part
        self.settings = settings
        self.root_model_part = self.model_part.GetRootModelPart()
        self.compute_model_part = self.root_model_part.GetSubModelPart(
            self.settings["compute_model_part_name"].GetString())

        # add moving load processes
        self.__add_moving_load_processes()

        # # remove condition of the original model part, as they are cloned
        self.__remove_cloned_conditions()

    def __add_moving_load_processes(self):
        """
        This function adds the moving load processes to the model part
        """
        count = 1
        for offset in self.settings["configuration"].values():
            # set moving load parameters
            moving_load_parameters = KratosMultiphysics.Parameters(self.settings).Clone()

            new_model_part_name = self.settings["model_part_name"].GetString().split('.')[-1] + "_cloned_" + str(count)
            new_model_part = self.__clone_moving_condition_in_compute_model_part(new_model_part_name)

            moving_load_parameters.AddString("model_part_name", new_model_part_name)
            moving_load_parameters.RemoveValue("configuration")
            moving_load_parameters.RemoveValue("active")
            moving_load_parameters.RemoveValue("compute_model_part_name")
            moving_load_parameters.AddValue("offset", offset.values()[0])

            # make sure the moving load process is serialized and cleared at finalize
            moving_load_parameters.AddBool("serialize", True)
            moving_load_parameters.AddBool("clear_at_finalize", True)

            self.moving_loads.append(StemSetMovingLoadProcess(new_model_part, moving_load_parameters))
            count += 1

    def __get_max_conditions_index(self):
        """
        This function returns the maximum index of the conditions in the main model part
        """
        max_index = 0
        for condition in self.model_part.GetRootModelPart().Conditions:
            if condition.Id > max_index:
                max_index = condition.Id
        return max_index

    def __clone_moving_condition_in_compute_model_part(self, new_body_part_name: str):
        """
        This function clones the moving load condition of the current model part to a new model part
        """

        # create new model part or get existing one
        if not self.compute_model_part.HasSubModelPart(new_body_part_name):
            new_model_part = self.compute_model_part.CreateSubModelPart(new_body_part_name)
        else:
            new_model_part = self.compute_model_part.GetSubModelPart(new_body_part_name)

        # set the point load to the value of the model part
        new_model_part.SetValue(KSM.POINT_LOAD, self.settings["load"].GetVector())

        # add nodes to the new model part
        node_ids = [node.Id for node in self.model_part.GetNodes()]
        new_model_part.AddNodes(node_ids)

        # add conditions to the new model part
        index = self.__get_max_conditions_index()
        for condition in self.model_part.Conditions:
            index += 1
            node_ids = [node.Id for node in condition.GetNodes()]

            geom = condition.GetGeometry()
            moving_load_name = CONDITION_NAME_MAP[(geom.WorkingSpaceDimension(), geom.PointsNumber())]

            new_model_part.CreateNewCondition(moving_load_name, index, node_ids, condition.Properties)

        return new_model_part

    def __remove_cloned_conditions(self):
        """
        This function removes the cloned conditions from the model part
        """
        for condition in self.model_part.Conditions:
            condition.Set(KratosMultiphysics.TO_ERASE, True)
        self.compute_model_part.RemoveConditions(KratosMultiphysics.TO_ERASE)

    def ExecuteInitialize(self):
        """
        This function initializes the moving load processes
        """
        if self.settings["active"].GetBool():
            for moving_load in self.moving_loads:
                moving_load.ExecuteInitialize()

    def ExecuteInitializeSolutionStep(self):
        """
        This function initializes the solution step of the moving load processes
        """
        if self.settings["active"].GetBool():
            for moving_load in self.moving_loads:
                moving_load.ExecuteInitializeSolutionStep()

    def ExecuteFinalizeSolutionStep(self):
        """
        This function finalizes the solution step of the moving load processes
        """
        if self.settings["active"].GetBool():
            for moving_load in self.moving_loads:
                moving_load.ExecuteFinalizeSolutionStep()

    def ExecuteFinalize(self):
        """
        This function finalizes the moving load processes and removes the moving load processes as required for
        multistage analysis
        """
        if self.settings["active"].GetBool():
            for i in reversed(range(len(self.moving_loads))):
                # finalize the moving load process
                self.moving_loads[i].ExecuteFinalize()
                # remove the moving load process, this is required for multistage analysis
                del self.moving_loads[i]

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

