import json

def uvec_test_stage_1(json_string):
    uvec_data = json.loads(json_string)

    uvec_data['loads'] = {1: [0, -30000, 0], 2: [0, -10000, 0]}
    return json.dumps(uvec_data)


def uvec_test_stage_2(json_string):
    uvec_data = json.loads(json_string)

    uvec_data['loads'] = {1: [0, -30000, 0], 2: [0, -10000, 0]}
    return json.dumps(uvec_data)