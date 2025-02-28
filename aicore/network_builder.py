import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from components.network_opt_algorithm.household_genetic_alg import get_household_network_solution
from components.network_opt_algorithm.business_genetic_algorithm import get_business_network_solution

def household_network_build(response, budget, number_of_devices, preferred_frequency, coverage_required, nation="Global", province="", brand_preference=[]):
    devices = get_household_network_solution(budget, number_of_devices, coverage_required, preferred_frequency, brand_preference, nation, province)
    return generate_network_response(response, devices)

def business_network_build(response, budget, number_of_devices, vlan_requirement, poe_devices, bandwidth_estimation, security_level, nation="Global", province=""):
    devices = get_business_network_solution(budget, number_of_devices, vlan_requirement, poe_devices, bandwidth_estimation, security_level, nation, province)
    return generate_network_response(response, devices)

def get_more_req(recommend_question):
    return {"response": recommend_question}

def get_graph(devices):
    genai.configure(api_key=os.environ["GEMINI_API"])
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config={
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        },
        tools=[
            genai.protos.Tool(
                function_declarations=[
                    genai.protos.FunctionDeclaration(
                        name="get_device_graph",
                        description="Create an estimation of network device graph and connection of nodes",
                        parameters=content.Schema(
                            type=content.Type.OBJECT,
                            required=["graph", "devices"],
                            properties={
                                "graph": content.Schema(
                                    type=content.Type.ARRAY,
                                    items=content.Schema(
                                        type=content.Type.OBJECT,
                                        required=["device_id", "connection_to"],
                                        properties={
                                            "device_id": content.Schema(type=content.Type.STRING),
                                            "connection_to": content.Schema(
                                                type=content.Type.ARRAY,
                                                items=content.Schema(type=content.Type.STRING),
                                            ),
                                        },
                                    ),
                                ),
                                "devices": content.Schema(
                                    type=content.Type.ARRAY,
                                    items=content.Schema(
                                        type=content.Type.OBJECT,
                                        required=["id", "name", "device_type", "quantity"],
                                        properties={
                                            "id": content.Schema(type=content.Type.STRING),
                                            "name": content.Schema(type=content.Type.STRING),
                                            "device_type": content.Schema(type=content.Type.STRING),
                                            "quantity": content.Schema(type=content.Type.INTEGER),
                                        },
                                    ),
                                ),
                            },
                        ),
                    ),
                ],
            ),
        ],
        tool_config={'function_calling_config': 'ANY'},
    )
    
    chat_session = model.start_chat()
    response = chat_session.send_message(", ".join([str(device) for device in devices]))
    args = dict(response.parts[0].function_call.args)
    return {
        "graph": [dict(i) for i in args['graph']],
        "devices": [dict(i) for i in args["devices"]],
    }

def generate_network_response(response, devices):
    cost = sum(float(i['price']) for i in devices)
    graph = get_graph(devices)
    img_urls = {i['id']: i['img_url'] for i in devices}
    
    for device in graph['devices']:
        device['img_url'] = img_urls[device['id']]
    
    return {
        "response": response,
        "networks": [
            {
                "type": "cost_opt",
                "devices": graph['devices'],
                "network_diagram": graph['graph'],
                "cost": cost,
            }
        ],
    }
