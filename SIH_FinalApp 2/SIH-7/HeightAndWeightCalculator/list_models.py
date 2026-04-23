import google.generativeai as genai

api_key = "AIzaSyAMr2HcsBfccN71gXRjPrSn_P-1hGmVmWs"
genai.configure(api_key=api_key)

print("Available Gemini models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
