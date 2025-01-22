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
          description = "khi câu nói của ngừoi dùng không liên quan đến chủ để về mạng và thiêt bị mạng thì sử dụng để trả lời như thông thường",
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
          description = "trả lời các vấn đề liên quan đến kĩ thuật về mạng hoặc thiết bị mạng",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = [],
            required = ["question"],
            properties = {
              "question": content.Schema(
                type = content.Type.STRING,
                description="nội dung câu hỏi (chuẩn hóa lại câu hỏi nếu cẩn thiết)"
              ),
            },
          ),
        ),
        genai.protos.FunctionDeclaration(
          name = "rcm_devices",
          description = "trả về các thiết bị khi người dùng yêu cầu các thiết bị mạng",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = [],
            required = ['query'],
            properties = {
              "budget": content.Schema(
                type = content.Type.NUMBER,
                description="Ngân sách dự kiến cho thiết bị mạng (USD)?"
              ),
              "query": content.Schema(
                  type = content.Type.STRING,
                  description="tối ưu câu truy vấn theo dạng 1 chuỗi requirement name: detail để truy vấn với vector database"
              )
            },
          ),
        ),
        genai.protos.FunctionDeclaration(
          name = "household_network_build",
          description = "đề xuất mạng lưới thiết bị tối ưu cho gia đình",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = [],
            required = ["budget", "number_of_devices", "preferred_frequency", "coverage_required"],
            properties = {
              "budget": content.Schema(
                type = content.Type.NUMBER,
                description="Ngân sách dự kiến cho hệ thống mạng (USD)?"
              ),
              "number_of_devices": content.Schema(
                type = content.Type.NUMBER,
              ),
              "preferred_frequency": content.Schema(
                type = content.Type.NUMBER,
                description = "ước tính tần số mà người dùng mong muốn (2.4Ghz, 5Ghz, 6Ghz) với đơn vị chuẩn là Mbps"
              ),
              "coverage_required": content.Schema(
                type = content.Type.NUMBER,
                description = "Ước tính diện tích phủ sóng với đơn vị chuẩn là m^2"
              ),
              "brand_preference": content.Schema(
                type = content.Type.STRING,
                enum=[]
              )
            },
          ),
        ),
        genai.protos.FunctionDeclaration(
          name = "get_more_req",
          description = "nếu các yêu cầu về mạng của người dùng chưa rõ ràng hoặc chưa đủ, tiếp tục hỏi để thu thập thông tin",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = [],
            required = ["recommend_question"],
            properties = {
              "recommend_question": content.Schema(
                type = content.Type.STRING,
                description="Câu hỏi đề xuất thêm các thông tin cần có của mạng hoặc thiết bị mà người dùng cần"
              ),
            },
          ),
        ),
        genai.protos.FunctionDeclaration(
          name = "business_network_build",
          description = "đề xuất mạng lưới thiết bị tối ưu cho doanh nghiệp",
          parameters = content.Schema(
            type = content.Type.OBJECT,
            enum = [],
            required = ["budget", "number_of_devices", "vlan_requirement", "poe_devices", "bandwidth_estimation", "security_level"],
            properties = {
              "budget": content.Schema(
                type = content.Type.NUMBER,
              ),
              "number_of_devices": content.Schema(
                type = content.Type.NUMBER
              ),
              "vlan_requirement": content.Schema(
                type = content.Type.BOOLEAN,
              ),
              "poe_devices": content.Schema(
                type = content.Type.NUMBER,
              ),
              "bandwidth_estimation": content.Schema(
                type = content.Type.NUMBER,
                description="ước tính băng thông của mạng (Mbps)"
              ),
              "security_level": content.Schema(
                type = content.Type.STRING,
                description="Mức độ bảo mật mong muốn? (Ví dụ: WPA3, VPN, Firewall)"
              ),
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
