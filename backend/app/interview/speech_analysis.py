FILLERS = ["um", "uh", "actually", "like", "you know"]

def analyze_speech(text):
    hesitations = [w for w in FILLERS if w in text.lower()]
    return {
        "hesitation_count": len(hesitations),
        "hesitations": hesitations
    }
