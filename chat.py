from aicore.planner import get_action, get_report
from aicore import device_rcm, normal_chat, technical_expert, network_builder

functions = {
    "normal_chat": normal_chat.normal_chat,
    "technical_chat": technical_expert.technical_chat,
    "rcm_devices": device_rcm.rcm_devices,
    "get_more_req": network_builder.get_more_req,
    "household_network_build": network_builder.household_network_build,
    "business_network_build": network_builder.business_network_build,
}

def get_response(history, nation="Global", province=""):
    res = {
        "status": "success",
        "response": "",
        "devices": [],
        "networks": [],
        "blogs": []
    }
    function = get_action(history, nation, province)
    function_dict = {
        'name': function[0],
        'args': function[1]
    }
    print(function_dict)
    result = functions[function_dict['name']](**function_dict['args'])
    for key in res.keys():
        if key in result.keys():
            res[key] = result[key]
    return res

def get_report_response(history):
    res = {
        "status": "success",
        "response": get_report(history)
    }
    return res