from app.services.llm import ask_llm

def evaluate_full_interview(qa_list, interview_type):
    system_prompt = """
You are a senior interview board.
Judge the candidate's complete interview performance.
"""

    user_prompt = f"""
Interview Type: {interview_type}

Q&A Transcript:
{qa_list}

Give:
- Overall percentage
- Communication score
- Technical score
- Confidence score
- Major mistakes
- Final improvement plan
"""

    return ask_llm(system_prompt, user_prompt)
