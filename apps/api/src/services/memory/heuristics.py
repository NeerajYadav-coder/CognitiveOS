from src.schemas.cognitive import CognitiveMemory
import re

def enforce_privacy_boundaries(memory: CognitiveMemory) -> CognitiveMemory:
    """
    Ensures that PII (Personally Identifiable Information) or overly sensitive
    surveillance data is stripped from the cognitive memory updates before storage.
    """
    pii_patterns = [
        r'\b\d{3}-\d{2}-\d{4}\b', # SSN
        r'\b[\w\.-]+@[\w\.-]+\.\w+\b', # Email
        r'\b\d{3}-\d{3}-\d{4}\b', # Phone (standard format)
        r'\b\d{10,15}\b' # Phone/Credit card approximations
    ]
    
    clean_events = []
    for event in memory.memory_events:
        content = event.content
        for pattern in pii_patterns:
            content = re.sub(pattern, "[REDACTED]", content)
        event.content = content
        clean_events.append(event)
        
    memory.memory_events = clean_events
    return memory

def prevent_cognitive_overfitting(memory: CognitiveMemory, historical_modes: list) -> CognitiveMemory:
    """
    Ensures that a user is allowed to evolve. If the historical modes are 'technical',
    and the new interaction is 'emotional', the engine shouldn't force 'technical' 
    back into the dominant modes.
    """
    # Just a pass-through for now, but in a real DB setting, this would compare
    # the new CognitiveProfileUpdates against the DB and ensure rapid shifts
    # in curiosity are preserved rather than averaged out.
    return memory
