import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from .model import generation_config

# Configure API key
genai.configure(api_key=os.getenv('GEMINI_API'))


# Function to create function declarations
def create_function_declaration(name, description, required, properties):
    return genai.protos.FunctionDeclaration(
        name=name,
        description=description,
        parameters=content.Schema(
            type=content.Type.OBJECT,
            required=required,
            properties=properties,
        ),
    )

SYSTEM_PROMPT = "You are NetExpert - A virtual network assistant expert."

# Define tool functions
tool_functions = [
    create_function_declaration(
        "normal_chat",
        f"{SYSTEM_PROMPT} Handles user questions unrelated to networking, responding cheerfully in a consultant tone.",
        ["response"],
        {"response": content.Schema(type=content.Type.STRING)},
    ),
    create_function_declaration(
        "technical_chat",
        f"{SYSTEM_PROMPT} Supports answering technical questions related to networks and telecommunications.",
        ["question"],
        {"question": content.Schema(type=content.Type.STRING, description="Standardized technical question.")},
    ),
    create_function_declaration(
        "rcm_devices",
        f"{SYSTEM_PROMPT} Provides expert recommendations for network devices based on user requirements, such as budget, performance needs, and specific use cases.",
        ["query", "response"],
        {
            "budget": content.Schema(
                type=content.Type.NUMBER,
                description=(
                    "The user's estimated budget in USD for purchasing network devices. This helps tailor recommendations to affordable and suitable options."
                ),),
            "query": content.Schema(
                type=content.Type.STRING,
                description=(
                    "An optimized search query designed for a vector database to retrieve relevant network device recommendations based on the user's requirements."
                ),),
            "response": content.Schema(
                type=content.Type.STRING,
                description=(
                    "A friendly and expert-level pre-recommendation statement that provides an engaging, consultative introduction before listing the suggested network devices."
                ),),},),
    create_function_declaration(
        "household_network_build",
        f"{SYSTEM_PROMPT} Recommends an optimal home network setup.",
        ["response", "budget", "number_of_devices", "preferred_frequency", "coverage_required"],
        {
            "budget": content.Schema(type=content.Type.NUMBER, description="Estimated budget (USD)."),
            "number_of_devices": content.Schema(type=content.Type.NUMBER),
            "preferred_frequency": content.Schema(type=content.Type.STRING, description="Preferred frequency (e.g., 2.4GHz, 5GHz)."),
            "coverage_required": content.Schema(type=content.Type.NUMBER, description="Coverage area in m²."),
            "brand_preference": content.Schema(type=content.Type.STRING),
            "response": content.Schema(type=content.Type.STRING, description="Pre-recommendation statement with a cheerful, friendly tone like an expert and consultant."),
            "nation": content.Schema(type=content.Type.STRING, description="Nation of the user."),
            "province": content.Schema(type=content.Type.STRING, description="Province of the user. If it is empty dont return anyone"),
        },
    ),
    create_function_declaration(
        "get_more_req",
        f"{SYSTEM_PROMPT} Requests additional network requirement details from the user if not enought info to build optimize network.",
        ["recommend_question"],
        {"recommend_question": content.Schema(type=content.Type.STRING, description="Clarifying question for the user with a cheerful, friendly tone like an expert and consultant.")},
    ),
    create_function_declaration(
        "business_network_build",
        f"{SYSTEM_PROMPT} Recommends optimal business network equipment.",
        ["response", "budget", "number_of_devices", "vlan_requirement", "poe_devices", "bandwidth_estimation", "security_level",],
        {
            "budget": content.Schema(type=content.Type.NUMBER),
            "number_of_devices": content.Schema(type=content.Type.INTEGER),
            "vlan_requirement": content.Schema(type=content.Type.STRING),
            "poe_devices": content.Schema(type=content.Type.INTEGER),
            "bandwidth_estimation": content.Schema(type=content.Type.NUMBER, description="Bandwidth estimate in Mbps."),
            "security_level": content.Schema(type=content.Type.STRING, description="Desired security level (e.g., WPA3, VPN)."),
            "response": content.Schema(type=content.Type.STRING, description="Pre-recommendation statement with a cheerful, friendly tone like an expert and consultant."),
            "nation": content.Schema(type=content.Type.STRING, description="Nation of the user."),
            "province": content.Schema(type=content.Type.STRING, description="Province of the user. If it is empty dont return any one"),
        },
    )
]

report_tool = [
    create_function_declaration(
        "get_report",
        f"""
            Generate a step-by-step tutorial on how to connect devices based on a given diagram.

            Returns:
            - str: A detailed tutorial guiding users on how to establish the connections described in the diagram.

            Features:
            - Identifies device roles and required equipment.
            - Provides instructions for both wired and wireless setups.
            - Covers network configuration (IP assignment, protocols, etc.).
            - Includes troubleshooting steps for common issues.
            - Supports different connection preferences (if specified).
        """,
        ['response'],
        {'response': content.Schema(type=content.Type.STRING, description="A detailed tutorial guiding users on how to establish the connections described in the diagram")}
    )
]
# Initialize Generative Model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-lite",
    generation_config=generation_config,
    tools=[genai.protos.Tool(function_declarations=tool_functions)],
    tool_config={'function_calling_config': 'ANY'},
)

report_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-lite",
    generation_config=generation_config,
    tools=[genai.protos.Tool(function_declarations=report_tool)],
    tool_config={'function_calling_config': 'ANY'},
)
# Function to get action based on history
def get_action(history, nation, province):
    print(history)
    chat_session = model.start_chat(history=history[:-2] if len(history) >= 2 else [])
    response = chat_session.send_message(history[-1]['parts'][0] + f"###USER LOCATION \nnation: {nation} \nprovince: {province}")
    return (response.parts[0].function_call.name, dict(response.parts[0].function_call.args)) if response.parts[0].function_call else None

def get_report(history):
    chat_session = report_model.start_chat(history=[])
    response = chat_session.send_message(history[-1]['parts'][0])
    return dict(response.parts[0].function_call.args)['response']
