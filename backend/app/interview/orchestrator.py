from app.database.db import SessionLocal
from app.database.crud import (
    get_or_create_user,
    create_interview,
    add_answer
)

def run_complete_interview(data):
    db = SessionLocal()

    user = get_or_create_user(
        db,
        name=data["name"],
        email=data["email"]
    )

    # LLM evaluation
    final_report = evaluate_full_interview(
        data["qa"],
        data["interview_type"]
    )

    interview = create_interview(
        db,
        user.id,
        data["interview_type"],
        data["mode"],
        data["level"],
        final_report["overall_percentage"]
    )

    for qa in data["qa"]:
        add_answer(
            db,
            interview.id,
            qa["question"],
            qa["answer"],
            qa["scores"]
        )

    db.close()
    return final_report
