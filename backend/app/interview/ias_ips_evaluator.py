from app.services.llm import ask_llm

def evaluate_ias_ips(answer):
    system_prompt = """
You are a UPSC interview board member.
Judge ethics, clarity, maturity.
"""

    user_prompt = f"""
Candidate Answer:
{answer}

Evaluate:
- Ethical reasoning (0-100)
- Decision maturity (0-100)
- Emotional control (0-100)
Explain briefly.
"""

    return ask_llm(system_prompt, user_prompt)
