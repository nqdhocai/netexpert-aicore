def household_network_build(budget, number_of_devices, preferred_frequency, brand_preference="None"):
    return {"networks":[
        {
            "type": "cost_opt",
            "devices": [
                {
                    "id": 'device id',
                    "quantity": 2,
                }
            ],
            "network_diagram": {
                "device id": ["device id"]
            },
            "cost": 1234
        }
    ]}


def business_network_build(budget, number_of_devices, vlan_requirement, poe_devices, bandwidth_estimation,
                           security_level):
    return {"networks": [
        {
            "type": "cost_opt",
            "devices": [
                {
                    "id": 'device id',
                    "quantity": 2,
                }
            ],
            "network_diagram": {
                "device id": ["device id"]
            },
            "cost": 1234
        }
    ]}


def get_more_req(recommend_question):
    return {"response": recommend_question}
