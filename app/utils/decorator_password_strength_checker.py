import re


def check_password_strength(password):
    score = 0
    feedback = []

    # Check length
    if len(password) < 8:
        feedback.append("Password is too short")
    elif len(password) >= 12:
        score += 2
        feedback.append("Good length")
    else:
        score += 1

    # Check for uppercase letters
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Add uppercase letters")

    # Check for lowercase letters
    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add lowercase letters")

    # Check for numbers
    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("Add numbers")

    # Check for special characters
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    else:
        feedback.append("Add special characters")

    # Check for repeating characters
    if re.search(r"(.)\1\1", password):
        score -= 1
        feedback.append("Avoid repeating characters")

    # Strength based on score
    if score < 2:
        strength = "Very Weak"
        color = "red"
    elif score < 4:
        strength = "Weak"
        color = "orange"
    elif score < 6:
        strength = "Medium"
        color = "yellow"
    elif score < 8:
        strength = "Strong"
        color = "lightgreen"
    else:
        strength = "Very Strong"
        color = "green"

    return strength, color, feedback
