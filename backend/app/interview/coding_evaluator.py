def evaluate_code_llm(code, language, question):
    system_prompt = """
You are a senior software engineer interviewer.
"""

    user_prompt = f"""
Language: {language}
Question:
{question}

Candidate Code:
{code}

Evaluate:
- Correctness
- Time Complexity
- Space Complexity
- Edge cases
- Code quality
- Optimization suggestions

Give score out of 100 and feedback.
"""

    return ask_llm(system_prompt, user_prompt)
