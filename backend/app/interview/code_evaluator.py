async def evaluate_code(code: str, expected_solution: str):
    """Evaluate code solution"""
    try:
        # Simple code evaluation - you can enhance this
        if not code or not code.strip():
            return 0, "No code provided"
        
        # Basic checks
        score = 50  # Default score
        
        # Check if code contains expected elements
        if expected_solution:
            expected_keywords = expected_solution.split()
            code_lower = code.lower()
            
            matches = sum(1 for keyword in expected_keywords if keyword.lower() in code_lower)
            score = min(100, (matches / len(expected_keywords)) * 100)
        
        feedback = f"Code received. Score: {score:.1f}%"
        if score < 60:
            feedback += " - Please review your solution."
        
        return score, feedback
        
    except Exception as e:
        print(f"Error evaluating code: {e}")
        return 50, "Unable to evaluate code due to technical issues."