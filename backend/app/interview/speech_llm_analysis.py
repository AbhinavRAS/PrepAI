from app.services.llm import ask_llm

def analyze_speech_llm(transcript):
    system_prompt = """
You are a professional speech and communication coach.
"""

    user_prompt = f"""
Transcript:
{transcript}

Detect:
- Filler words
- Hesitations
- Confidence issues
Suggest corrections.
"""

    return ask_llm(system_prompt, user_prompt)
