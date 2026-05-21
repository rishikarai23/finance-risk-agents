import os
import json
from dotenv import load_dotenv
from groq import Groq
from core.context import FinancialContext
import praw

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

