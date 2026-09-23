from src.schemas.cognitive import CognitiveReflection

def protect_against_diagnosis(reflection: CognitiveReflection) -> CognitiveReflection:
    """
    Strips psychological terminology and prevents identity classification.
    """
    diagnostic_words = ["adhd", "depressed", "anxious", "disorder", "neurotic", "obsessive"]
    
    clean_trends = []
    for trend in reflection.reflection_summary.exploration_trends:
        if not any(word in trend.lower() for word in diagnostic_words):
            clean_trends.append(trend)
        else:
            clean_trends.append("Highly variable conceptual exploration.")
            
    reflection.reflection_summary.exploration_trends = clean_trends
    return reflection

def reframe_blind_spots(reflection: CognitiveReflection) -> CognitiveReflection:
    """
    Ensures blind spots are framed as 'areas of inquiry' rather than 'flaws'.
    """
    reframed = []
    for spot in reflection.possible_blind_spots:
        # Instead of "User ignores X", it reframes to "Potential exploration of X"
        if "ignores" in spot.lower() or "lacks" in spot.lower():
            spot = spot.replace("ignores", "has not yet explored").replace("lacks", "might benefit from")
        reframed.append(spot)
        
    reflection.possible_blind_spots = reframed
    return reflection
