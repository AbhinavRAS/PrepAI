from app.services.llm import ask_llm

def evaluate_answer(question, answer, interview_type):
    system_prompt = """
You are an AI interview evaluator.
Judge answers strictly and professionally.
"""

    user_prompt = f"""
Interview Type: {interview_type}

Question:
{question}

Candidate Answer:
{answer}

Evaluate on:
1. Communication (0-100)
2. Confidence (0-100)
3. Technical Accuracy (0-100)
4. Pronunciation / Fluency (0-100)

Also provide:
- Mistakes
- Missed points
- Better version of answer
- Final short feedback
Return JSON only.
"""

    result = ask_llm(system_prompt, user_prompt)
    return result

