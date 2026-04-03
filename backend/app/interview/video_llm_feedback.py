from app.services.llm import ask_llm

def generate_video_feedback(posture_score, gesture_summary):
    system_prompt = """
You are a body language and interview presence expert.
"""

    user_prompt = f"""
Posture Score: {posture_score}
Gesture Summary: {gesture_summary}

Judge interview suitability and suggest corrections.
"""

    return ask_llm(system_prompt, user_prompt)
