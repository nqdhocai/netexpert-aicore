import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from ast import literal_eval

from components.network_opt_algorithm.household_genetic_alg import get_household_network_solution

def household_network_build(budget, number_of_devices, preferred_frequency, coverage_required, brand_preference=[]):
    devices = get_household_network_solution(budget, number_of_devices, coverage_required, preferred_frequency, brand_preference)
    cost = sum([float(i['price']) for i in devices])
    graph = get_graph(devices)

    img_urls = {
        i['id']: i['img_url'] for i in devices
    }
    for device in graph['devices']:
        device['img_url'] = img_urls[device['id']]
    return {"networks": [
        {
            "type": "cost_opt",
            "devices": graph['devices'],
            "network_diagram": graph['graph'],
            "cost": cost
        }
    ]}


def business_network_build(budget, number_of_devices, vlan_requirement, poe_devices, bandwidth_estimation, security_level):
    devices = get_household_network_solution(budget, number_of_devices, 0, 0, brand_preference=[])
    cost = sum([float(i['price']) for i in devices])
    graph = get_graph(devices)
    return {"networks": [
        {
            "type": "cost_opt",
            "devices": graph['devices'],
            "network_diagram": graph['graph'],
            "cost": cost
        }
    ]}


def get_more_req(recommend_question):
    return {"response": recommend_question}


def get_graph(devices):
    genai.configure(api_key=os.environ["GEMINI_API"])

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        tools=[
            genai.protos.Tool(
                function_declarations=[
                    genai.protos.FunctionDeclaration(
                        name="get_device_graph",
                        description="create a estimation of network device graph and connection of nodes",
                        parameters=content.Schema(
                            type=content.Type.OBJECT,
                            enum=[],
                            required=["graph", "devices"],
                            properties={
                                "graph": content.Schema(
                                    type=content.Type.ARRAY,
                                    items=content.Schema(
                                        type=content.Type.OBJECT,
                                        enum=[],
                                        required=["device_id", "connection_to"],
                                        properties={
                                            "device_id": content.Schema(
                                                type=content.Type.STRING,
                                            ),
                                            "connection_to": content.Schema(
                                                type=content.Type.ARRAY,
                                                items=content.Schema(
                                                    type=content.Type.STRING,
                                                ),
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
                                            "id": content.Schema(
                                                type=content.Type.STRING,
                                            ),
                                            "name": content.Schema(
                                                type=content.Type.STRING,
                                            ),
                                            "device_type": content.Schema(
                                                type=content.Type.STRING,
                                            ),
                                            "quantity": content.Schema(
                                                type=content.Type.INTEGER,
                                            )
                                        },
                                    ), )
                            },
                        ),
                    ),
                ],
            ),
        ],
        tool_config={'function_calling_config': 'ANY'},
    )
    chat_session = model.start_chat()
    devices = [str(device) for device in devices]
    devices = ", ".join(devices)
    response = chat_session.send_message(devices)
    args = dict(response.parts[0].function_call.args)
    network_graph = {
        "graph": [dict(i) for i in args['graph']],
        "devices": [dict(i) for i in args["devices"]],
    }
    return network_graph
