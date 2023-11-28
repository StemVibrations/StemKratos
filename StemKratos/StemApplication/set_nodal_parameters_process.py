import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as KSM

# Set available nodal parameter options
NODAL_PARAMETER_OPTIONS = [KSM.NODAL_DAMPING_RATIO, KSM.NODAL_DISPLACEMENT_STIFFNESS,
                           KSM.NODAL_ROTATIONAL_DAMPING_RATIO,
                           KSM.NODAL_ROTATIONAL_STIFFNESS, KratosMultiphysics.NODAL_MASS]


class SetNodalParametersProcess(KratosMultiphysics.Process):
    """
    This process sets the nodal parameters of the model part. The nodal parameters are set to the values of the
    properties of the model part.

    Inheritance:
        - :class:`KratosMultiphysics.Process`

    Attributes:
        - model_part (KratosMultiphysics.ModelPart): model part containing the elements
        - settings (KratosMultiphysics.Parameters): settings of the process


    """

    def __init__(self, model_part: KratosMultiphysics.ModelPart, settings: KratosMultiphysics.Parameters):
        """
        Initialize process

        Args:
            - model_part (KratosMultiphysics.ModelPart): model part containing the elements
            - settings (KratosMultiphysics.Parameters): settings of the process
        """
        KratosMultiphysics.Process.__init__(self)
        self.model_part = model_part
        self.settings = settings

    def ExecuteInitialize(self):
        """
        This function sets the nodal parameters of the model part. The nodal parameters are set to the values of the
        properties of the model part. This function name cannot be changed. This name is recognised by Kratos.
        """

        # get properties of the model part
        model_part_properties = [property for property in self.model_part.Properties][0]

        # get available nodal parameters
        available_nodal_parameters = [parameter for parameter in NODAL_PARAMETER_OPTIONS if
                                      model_part_properties.Has(parameter)]

        # set nodal parameters on each element
        for element in self.model_part.Elements:
            for parameter in available_nodal_parameters:
                element.SetValue(parameter, model_part_properties.GetValue(parameter))


def Factory(settings: KratosMultiphysics.Parameters, model: KratosMultiphysics.Model) -> SetNodalParametersProcess:
    """
    This function creates a process setting the nodal parameters of the model part. The nodal parameters are set to the
    values of the properties of the model part. This function name cannot be changed. This name is recognised by Kratos.

    Args:
        - settings (KratosMultiphysics.Parameters): settings of the process
        - model (KratosMultiphysics.Model): Kratos model containing the model part

    raises:
        - Exception: if the settings are not correct

    returns:
        - :class:`SetNodalParametersProcess`: process setting the nodal parameters of the model part
    """

    # checks if the input is a Parameters object, encapsulating a json string
    if not isinstance(settings, KratosMultiphysics.Parameters):
        raise Exception("expected input shall be a Parameters object, encapsulating a json string")

    # Get default settings
    default_settings = KratosMultiphysics.Parameters("""
            {
                "model_part_name" : "please_specify_model_part_name"
            }
            """
                                                     )

    # Overwrite the default settings with user-provided parameters
    process_settings = settings["Parameters"]

    # Validate settings
    process_settings.ValidateAndAssignDefaults(default_settings)

    # Set process
    model_part = model.GetModelPart(process_settings["model_part_name"].GetString())
    return SetNodalParametersProcess(model_part, process_settings)
