import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()

import os


genai.configure(api_key=os.getenv('GEMINI_API'))

# Create the model
generation_config = {
  "temperature": 0.95,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

function_calling_model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-lite",
  generation_config=generation_config,
)

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-thinking-exp-01-21",
  generation_config=generation_config,
)