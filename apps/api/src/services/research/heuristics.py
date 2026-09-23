from src.schemas.cognitive import ResearchState, ExplorationTree, ResearchNode

MAX_RESEARCH_DEPTH = 3
MAX_BRANCHES = 5

def enforce_bounded_exploration(state: ResearchState) -> ResearchState:
    """
    Prevents uncontrolled recursive research expansion.
    Enforces a hard ceiling on tree depth and branch count.
    Any nodes exceeding the depth limit are forcefully marked 'abandoned'.
    """
    pruned_branches = []
    for node in state.research_tree.branches:
        if node.depth_level > MAX_RESEARCH_DEPTH:
            node.status = "abandoned"
        pruned_branches.append(node)
    
    # Cap total branch count
    if len(pruned_branches) > MAX_BRANCHES:
        for overflow_node in pruned_branches[MAX_BRANCHES:]:
            overflow_node.status = "abandoned"
            
    state.research_tree.branches = pruned_branches
    return state

def detect_circular_inquiry(state: ResearchState) -> ResearchState:
    """
    Detects if the LLM generated duplicate sub-inquiries, which would create
    an infinite conceptual loop. De-duplicates by inquiry text.
    """
    seen_inquiries = set()
    unique_branches = []
    for node in state.research_tree.branches:
        normalized = node.inquiry.strip().lower()
        if normalized not in seen_inquiries:
            seen_inquiries.add(normalized)
            unique_branches.append(node)
        # Silently drop duplicates
        
    state.research_tree.branches = unique_branches
    return state

def flag_speculative_synthesis(state: ResearchState) -> ResearchState:
    """
    If the synthesized understanding uses high-confidence language but the
    research confidence is low, we inject an honest uncertainty disclaimer.
    """
    if state.synthesized_understanding and state.confidence < 0.6:
        speculative_phrases = ["certainly", "definitively", "without doubt", "proven"]
        for phrase in speculative_phrases:
            if phrase in state.synthesized_understanding.lower():
                state.synthesized_understanding += " [NOTE: This synthesis has low confidence and should be treated as exploratory, not conclusive.]"
                break
    return state
