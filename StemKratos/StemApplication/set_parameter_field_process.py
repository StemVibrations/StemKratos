import warnings
from typing import Optional

import KratosMultiphysics
import KratosMultiphysics.GeoMechanicsApplication as KratosGeo
from KratosMultiphysics.GeoMechanicsApplication.set_parameter_field_process import SetParameterFieldProcess

#todo bring functionalities from this class to the parent class and remove this class  #29
class StemSetParameterFieldProcess(SetParameterFieldProcess):
    """
    Sets parameter field process. This process has 3 option to generate a custom parameter field:

    | option 1, func_type = 'input': with this option, a parameter field is generated based on a function which is
    directly written in the projectparameters.json at the 'function' parameter. This function can depend on
    the x, y and z coordinate.

    | option 2, func_type = 'python': with this option, a parameter field is generated, using a user defined python
    script. This python script has to be inherited from the 'ParameterFieldBase' class. Which is located at:
    'GeoMechanicsApplication->python_scripts->user_defined_scripts->user_defined_parameter_field_base.py'
    the name of the script (without '.py') should be filled in at the 'function' parameter in the projectparameters.json

    | option 3, func_type = 'json_file': with this option, a parameter field can be directly read from a json dictionary.
    This dictionary has to contain the 'values' key, which is a 1D list of all the field values. The list has to have
    the same size as the elements within the model part, and need to be accordingly sorted. The filename should be
    filled in at the 'dataset' parameter, within the projectparameters.json

    Inheritance:
        - :class:`KratosMultiphysics.GeoMechanicsApplication.set_parameter_field_process.SetMovingLoadProcess`
    """

    def __init__(self, model: KratosMultiphysics.Model, settings: KratosMultiphysics.Parameters):
        """
        Constructor of the StemSetParameterFieldProcess

        Args:
            - model (KratosMultiphysics.Model): the model containing the model part
            - settings (KratosMultiphysics.Parameters): the settings of the process
        """
        super().__init__(model, settings)

    def GetVariableBasedOnString(self) -> Optional[KratosMultiphysics.VariableData]:
        """
        This function returns the variable based on the variable name string.

        Returns:
            - Optional[KratosMultiphysics.VariableData]: the kratos variable object
        """

        # Get variable object
        imported_modules = [KratosGeo, KratosMultiphysics]

        for kratos_module in imported_modules:
            if hasattr(kratos_module, self.params["variable_name"].GetString()):
                variable = getattr(kratos_module, self.params["variable_name"].GetString())
                return variable

        # add warning if variable is not found
        warnings.warn(f'The variable: {self.params["variable_name"].GetString()} is not present within '
                        f'the imported modules')
        return None
