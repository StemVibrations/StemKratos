from typing import Dict, Any

import json
import os
import importlib.util

import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as KSM


class StemUvecController:

    def __init__(self, uvec_data, model_part):

        self.uvec_path = uvec_data["uvec_path"].GetString()
        self.uvec_method = uvec_data["uvec_method"].GetString()
        self.uvec_base_model_part = uvec_data["uvec_model_part"].GetString()

        # Create a spec object for the module
        module_name = os.path.basename(self.uvec_path).split(".")[0]
        spec = importlib.util.spec_from_file_location(module_name, self.uvec_path)

        # Create the module from the spec
        uvec = importlib.util.module_from_spec(spec)

        # Load the module
        spec.loader.exec_module(uvec)
        self.callback_function = getattr(uvec, self.uvec_method)

        # get correct conditions
        self.axle_model_parts = []
        for part in model_part.SubModelParts:
            if (self.uvec_base_model_part + "_cloned_") in part.Name:
                self.axle_model_parts.append(model_part.GetSubModelPart(part.Name))

    def initialise_solution_step(self, json_data: KratosMultiphysics.Parameters):
        """
        This function initialises the solution step in case a UVEC model is used.

        Args:
            - json_data (KratosMultiphysics.Parameters): input data for the UVEC model
        """

        if len(self.axle_model_parts) > 0:

            if not json_data.Has("dt"):
                json_data.AddEmptyValue("dt")
            json_data.AddDouble("dt", self.axle_model_parts[0].ProcessInfo[KratosMultiphysics.DELTA_TIME])

            if not json_data.Has("t"):
                json_data.AddEmptyValue("t")
            json_data.AddDouble("t", self.axle_model_parts[0].ProcessInfo[KratosMultiphysics.TIME])

            if not json_data.Has("time_index"):
                json_data.AddEmptyValue("time_index")
            json_data.AddInt("time_index", self.axle_model_parts[0].ProcessInfo[KratosMultiphysics.STEP] - 1)

    def execute_uvec_update_kratos(self, json_data: KratosMultiphysics.Parameters) -> KratosMultiphysics.Parameters:
        """
        This function calls the uvec model and updates the Kratos model with the result.

        Args:
            - json_data (KratosMultiphysics.Parameters): input data for the uvec model

        Returns:
            - KratosMultiphysics.Parameters: output data from the uvec model

        """

        # add empty variables to uvec input data
        # make sure all axles have required empty data structure
        required_axle_parameters = ["u", "theta", "loads"]
        for axle in self.axle_model_parts:
            axle_number = (axle.Name.split("_")[-1])
            for variable_json in required_axle_parameters:
                self.add_empty_variable_to_parameters(json_data, axle_number, variable_json)

        # call uvec function
        uvec_json = KratosMultiphysics.Parameters(self.callback_function(json_data.WriteJsonString()))

        # add loads from uvec to the model
        for axle in self.axle_model_parts:
            axle_number = (axle.Name.split("_")[-1])

            # set value on model part
            axle.SetValue(KSM.POINT_LOAD, uvec_json["loads"][axle_number].GetVector())

            # transfer load from model part to conditions
            self.__transfer_load_from_model_part_to_conditions(axle)

        return uvec_json

    def getMovingConditionVariable(self, axle, Variable):
        # This assumes that only one condition contains the moving load has values:
        values = [0.0, 0.0, 0.0]
        for condition in axle.Conditions:
            cond_values = condition.GetValue(Variable)
            for i in range(3):
                values[i] += cond_values[i]
        return KratosMultiphysics.Vector(values)

    def add_empty_variable_to_parameters(self,
                                         json_data: KratosMultiphysics.Parameters,
                                         axle_number: str,
                                         variable_json: str):
        """
        This function adds an empty variable to the parameters.

        Args:
            - json_data (KratosMultiphysics.Parameters): input data for the uvec model
            - axle_number (str): number of the axle
            - variable_json (str): variable to be added to the parameters

        """
        if not json_data.Has(variable_json):
            json_data.AddEmptyValue(variable_json)
        if not json_data[variable_json].Has(axle_number):
            json_data[variable_json].AddValue(axle_number, KratosMultiphysics.Parameters("[]"))

    def update_uvec_variable_from_kratos(self,
                                         json_data: KratosMultiphysics.Parameters,
                                         axle_number: str,
                                         axle_model_part: KratosMultiphysics.ModelPart,
                                         variable_json: str,
                                         variable_kratos: KratosMultiphysics.Array1DVariable3):
        """
        This function updates the UVEC variable from Kratos.

        Args:
            - json_data (KratosMultiphysics.Parameters): input data for the uvec model
            - axle_number (str): number of the axle
            - axle_model_part (KratosMultiphysics.ModelPart): model part containing the conditions
            - variable_json (str): variable to be added to the parameters
            - variable_kratos (KratosMultiphysics.Array1DVariable3): variable to be added to the parameters

        """

        self.add_empty_variable_to_parameters(json_data, axle_number, variable_json)
        json_data[variable_json][axle_number].SetVector(self.getMovingConditionVariable(axle_model_part, variable_kratos))

    def update_uvec_from_kratos(self, json_data: KratosMultiphysics.Parameters):
        """
        This function updates the UVEC data with the displacement and rotation from Kratos.

        Args:
            - json_data (KratosMultiphysics.Parameters): input data for the uvec model

        """
        # get data from each axle
        for axle_model_part in self.axle_model_parts:
            axle_number = (axle_model_part.Name.split("_")[-1])

            # get displacement and rotation at the axle contact points in Kratos
            self.update_uvec_variable_from_kratos(
                json_data, axle_number, axle_model_part, "u", KratosMultiphysics.DISPLACEMENT)
            self.update_uvec_variable_from_kratos(
                json_data, axle_number, axle_model_part, "theta", KratosMultiphysics.ROTATION)

    @staticmethod
    def __transfer_load_from_model_part_to_conditions(model_part: KratosMultiphysics.ModelPart, precision=1e-12):
        """
        This function transfers the point load from the model part to the condition which contains a non-zero value.

        Args:
            - model_part (KratosMultiphysics.ModelPart): model part containing the conditions
            - precision (float): precision for the zero check
        """

        for condition in model_part.Conditions:
            if not all(abs(load_magnitude) < precision for load_magnitude in condition.GetValue(KSM.POINT_LOAD)):
                condition.SetValue(KSM.POINT_LOAD, model_part.GetValue(KSM.POINT_LOAD))
