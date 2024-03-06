import json

def uvec_test(json_string):
    uvec_data = json.loads(json_string)

    uvec_data['loads'] = {1: [0, -30, 0], 2: [0, -10, 0]}
    return json.dumps(uvec_data)
    