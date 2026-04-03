import asyncio
import os
import traceback
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

async def test():
    try:
        client = AsyncOpenAI(base_url='https://api.groq.com/openai/v1', api_key=os.getenv('GROQ_API_KEY'))
        r = await client.chat.completions.create(model='llama-3.3-70b-versatile', messages=[{'role': 'user', 'content': 'Test'}], temperature=0.7)
        print("SUCCESS:", r.choices[0].message.content)
    except Exception as e:
        print("FULL EXCEPTION:", str(e))
        print("REPR:", repr(e))

if __name__ == "__main__":
    asyncio.run(test())
