import os
import google.generativeai as genai

class BaseAgent(object):
    def __init__(self, role, description, llm=None):
        if llm != None:
            self.llm = llm
        else:
            self.init_llm()
        self.role = role
        self.description = description
    def init_llm(self):
        GEMINI_API = os.getenv('GEMINI_API')
        genai.configure(api_key=GEMINI_API)

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
        )
        self.llm = model

agent = BaseAgent(role="", description="")
print(agent.llm)