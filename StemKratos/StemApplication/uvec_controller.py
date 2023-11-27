import json
import os
import importlib.util
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as KSM

class StemUvecController:

    def __init__(self, uvec_data, model_part):

        self.uvec_path = uvec_data["uvec_path"].GetString()
        self.uvec_method= uvec_data["uvec_method"].GetString()
        self.uvec_base_model_part = uvec_data["uvec_model_part"].GetString()

        print("============================================================")
        print("STEM UVEC CONTROLLER")
        print("============================================================")
        print(" uvec_path: ", self.uvec_path)
        print(" uvec_method: ", self.uvec_method)
        print(" uvec_base_model_part: ", self.uvec_base_model_part)
        print("============================================================")

        # Create a spec object for the module
        module_name = os.path.basename(self.uvec_path).split(".")[0]
        spec = importlib.util.spec_from_file_location(module_name, self.uvec_path)

        # Create the module from the spec
        uvec = importlib.util.module_from_spec(spec)

        # Load the module
        spec.loader.exec_module(uvec)
        self.callback_function = getattr(uvec, self.uvec_method)

        #get correct conditions
        self.axle_model_parts = []
        for part in model_part.SubModelParts:
            if (self.uvec_base_model_part + "_cloned_") in part.Name:
                self.axle_model_parts.append(model_part.GetSubModelPart(part.Name))
                print("Info: STEM_UVEC_CONTROLLER:: Added ", part.Name)

    def update_dt(self, json_data):
        if not json_data.Has("dt"):
            json_data.AddEmptyValue("dt")
        json_data.AddDouble("dt", self.axle_model_parts[0].ProcessInfo[KratosMultiphysics.DELTA_TIME])
        if not json_data.Has("t"):
            json_data.AddEmptyValue("t")
        json_data.AddDouble("t", self.axle_model_parts[0].ProcessInfo[KratosMultiphysics.TIME])
        if not json_data.Has("time_index"):
            json_data.AddEmptyValue("time_index")
        json_data.AddInt("time_index", self.axle_model_parts[0].ProcessInfo[KratosMultiphysics.STEP] - 1)

    def execute_uvec_update_kratos(self, json_data):
        # make sure all axles have required empty data structure
        required_axle_parameters = ["u", "theta", "loads"]
        for axle in self.axle_model_parts:
            axle_number = (axle.Name.split("_")[-1])
            for variable_json in required_axle_parameters:
                self.add_empty_variable_to_parameters(json_data, axle_number, axle, variable_json)
        uvec_json = KratosMultiphysics.Parameters(self.callback_function(json_data.WriteJsonString()))
        for axle in self.axle_model_parts:
            axle_number = (axle.Name.split("_")[-1])
            axle.SetValue(KSM.POINT_LOAD, uvec_json["loads"][axle_number].GetVector())
        return uvec_json

    def getMovingConditionVariable(self, axle, Variable):
        # This assumes that only one condition contains the moving load has values:
        values = [0.0, 0.0, 0.0]
        for condition in axle.Conditions:
            cond_values = condition.GetValue(Variable)
            for i in range(3):
                values[i] += cond_values[i]
        return KratosMultiphysics.Vector(values)

    def add_empty_variable_to_parameters(self, json_data, axle_number, axle, variable_json):
        if not json_data.Has(variable_json):
            json_data.AddEmptyValue(variable_json)
        if not json_data[variable_json].Has(axle_number):
            json_data[variable_json].AddValue(axle_number, KratosMultiphysics.Parameters("[]"))
    def update_uvec_variable_from_kratos(self, json_data, axle_number, axle, variable_json, variable_kratos):
        self.add_empty_variable_to_parameters(json_data, axle_number, axle, variable_json)
        json_data[variable_json][axle_number].SetVector(self.getMovingConditionVariable(axle, variable_kratos))

    def update_uvec_from_kratos(self, json_data):
        # get data from each axle
        for axle in self.axle_model_parts:
            axle_number = (axle.Name.split("_")[-1])
            self.update_uvec_variable_from_kratos(json_data, axle_number, axle, "u", KratosMultiphysics.DISPLACEMENT)
            self.update_uvec_variable_from_kratos(json_data, axle_number, axle, "theta", KratosMultiphysics.ROTATION)
        return json_data

if __name__ == "__main__":
    import KratosMultiphysics as KM

    uvec_params = KM.Parameters("""{
        "uvec_path"                     :     "C:/Users/jdnut/Desktop/StemPython/UVEC/my_sample_uvec.py",
        "uvec_method"				    :     "uvec_test",
        "uvec_data"						:     "{'dt': 0.0, 'u':{}, 'theta':{}, 'loads':{}, 'parameters' :{}, 'state':{}}"
    }""")

    controller = StemUvecController(uvec_params)
    json_test_string = json.dumps({"test": "test"})
    print(json.loads(json_test_string))
    json_test_string = controller.callback_function(json_test_string)
    print(json.loads(json_test_string))
