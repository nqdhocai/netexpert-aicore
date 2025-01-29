"""
Install an additional SDK for JSON schema support Google AI Python SDK

$ pip install google.ai.generativelanguage
"""

import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

genai.configure(api_key=os.getenv('GEMINI_API'))

# Create the model
generation_config = {
  "temperature": 0.95,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}


model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
  tools = [
    genai.protos.Tool(
      function_declarations = [
        genai.protos.FunctionDeclaration(
          name = "normal_chat",
          description = "Handles user questions or statements that are not related to networking, network equipment, or the Telecommunications field. This function will respond in a normal manner, appropriate to the next issues of the day. (*Note: Use a product consultant tone of voice)",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = [],
            required = ["response"],
            properties = {
              "response": content.Schema(
                type = content.Type.STRING,
              ),
            },
          ),
        ),
        genai.protos.FunctionDeclaration(
          name = "technical_chat",
          description = "Support answering technical questions related to computer networks, network equipment, and telecommunications issues. The system has the ability to automatically standardize questions to ensure accurate and contextual answers. Suitable for both individual users and technical experts.",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = [],
            required = ["question"],
            properties = {
              "question": content.Schema(
                type = content.Type.STRING,
                description="The content of the question that needs to be answered. The system will automatically standardize the question (if necessary) to optimize the processing."
              ),
            },
          ),
        ),
        genai.protos.FunctionDeclaration(
          name = "rcm_devices",
          description = "Returns devices when user requests network devices",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = [],
            required = ['query', "response"],
            properties = {
              "budget": content.Schema(
                type = content.Type.NUMBER,
                description="Estimated budget for network equipment (USD)?"
              ),
              "query": content.Schema(
                  type = content.Type.STRING,
                  description="Optimize query in the form of a string requirement name: detail to query with vector database"
              ),
              "response": content.Schema(
                type = content.Type.STRING,
                description = "statements before product recommendation. (*Note: Use a product consultant tone of voice)"
              )
            },
          ),
        ),
        genai.protos.FunctionDeclaration(
          name = "household_network_build",
          description = "Recommend the optimal network of devices for your home",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = [],
            required = ["response", "budget", "number_of_devices", "preferred_frequency", "coverage_required"],
            properties = {
              "budget": content.Schema(
                type = content.Type.NUMBER,
                description="Estimated budget for network system (USD)?"
              ),
              "number_of_devices": content.Schema(
                type = content.Type.NUMBER,
              ),
              "preferred_frequency": content.Schema(
                type = content.Type.STRING, #[TODO] fix algorithm to use this parameter type as NUMBER, not string
                description = "Estimate the frequency that the user wants (2.4Ghz, 5Ghz, 6Ghz) with the standard unit of Mbps"
              ),
              "coverage_required": content.Schema(
                type = content.Type.NUMBER,
                description = "Estimate coverage area with standard unit of m^2"
              ),
              "brand_preference": content.Schema(
                type = content.Type.STRING,
                enum=[]
              ),
              "response": content.Schema(
                type = content.Type.STRING,
                description = "statement before suggesting network equipment that the user requires.  (*Note: Use a product consultant tone of voice)"
              )
            },
          ),
        ),
        genai.protos.FunctionDeclaration(
          name = "get_more_req",
          description = "If the user's network requirements are unclear or insufficient, continue asking to gather information.",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = [],
            required = ["recommend_question"],
            properties = {
              "recommend_question": content.Schema(
                type = content.Type.STRING,
                description="The question suggests additional information about the network or device that the user needs. (*Note: Use a product consultant tone of voice)"
              ),
            },
          ),
        ),
        genai.protos.FunctionDeclaration(
          name = "business_network_build",
          description = "Recommend optimal network equipment for business",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = [],
            required = ["response", "budget", "number_of_devices", "vlan_requirement", "poe_devices", "bandwidth_estimation", "security_level"],
            properties = {
              "budget": content.Schema(
                type = content.Type.NUMBER,
              ),
              "number_of_devices": content.Schema(
                type = content.Type.INTEGER
              ),
              "vlan_requirement": content.Schema(
                type = content.Type.STRING,
              ),
              "poe_devices": content.Schema(
                type = content.Type.INTEGER,
              ),
              "bandwidth_estimation": content.Schema(
                type = content.Type.NUMBER,
                description="network bandwidth estimate (renormalized to Mbps)"
              ),
              "security_level": content.Schema(
                type = content.Type.STRING,
                description="What level of security is desired? (Examples: WPA3, VPN, Firewall)"
              ),
              "response": content.Schema(
                type = content.Type.STRING,
                description = "statement before suggesting network equipment that the user requires. (*Note: Use a product consultant tone of voice)"
              )
            },
          ),
        ),
      ],
    ),
  ],
  tool_config={'function_calling_config':'ANY'},
)

def get_action(history):
    print(history)
    if len(history) >= 2:
        chat_session = model.start_chat(
            history = history[0:-2],
        )
    else:
        chat_session = model.start_chat()
    response = chat_session.send_message(history[-1]['parts'][0])
    if fn := response.parts[0].function_call:
        return (fn.name, dict(fn.args))
    else:
        return None
