def recommend_glasses(face_shape):
    shape = face_shape.lower()
    if shape == "round":
        return [
            "Square round rames to add definition.",
            "Cat-eye styles to lift the face.",
            "Bold, geometric designs to contrast curves."
        ]
    elif shape == "oval":
        return [
            "Round square to balance long face.",
            "Square for balance.",
            "Bold to highlight cheekbones."
        ]
    elif shape == "square":
        return [
            "Oval frames to soften angles.",
            "Curved cateye styles to add contrast.",
            "Rimless glasses for a subtle touch."
        ]
    elif shape == "diamond":
        return [
            "Heavy frames to balance cheekbones.",
            "Round for softness.",
            "Cat-eye for emphasis on brow line."
        ]
    else:
        return [
            "Neutral glasses styles recommended.",
            "Try round or rectangular styles.",
            "Avoid extremes in shape."
        ]
