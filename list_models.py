import os, sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

try:
    models = client.models.list()
    # Filter for gpt-5 or o1/o3/reasoning models
    relevant = [m.id for m in models.data if 'gpt-5' in m.id or 'o1' in m.id or 'o3' in m.id or '4.5' in m.id]
    print("Available advanced models:", relevant)
except Exception as e:
    print("Error:", e)
