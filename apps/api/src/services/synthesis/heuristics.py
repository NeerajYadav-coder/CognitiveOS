from src.schemas.cognitive import PromptSynthesis, ClarificationStrategy

def inject_clarification_constraints(synthesis: PromptSynthesis, strategy: ClarificationStrategy) -> PromptSynthesis:
    """
    If the Ambiguity engine determined clarification is needed, 
    the synthesized prompt MUST explicitly ask the LLM to ask the user questions 
    before answering the objective.
    """
    if strategy and strategy.enabled:
        constraint = f"BEFORE answering, you MUST ask {strategy.question_count} clarifying questions to the user at a {strategy.depth} depth level."
        if constraint not in synthesis.prompt_structure.constraints:
            synthesis.prompt_structure.constraints.append(constraint)
            
        # Re-build final prompt string to ensure constraint is present
        if "BEFORE answering" not in synthesis.final_prompt:
            synthesis.final_prompt = f"{constraint}\n\n" + synthesis.final_prompt
            synthesis.optimization_notes.append("Injected clarification constraint based on Ambiguity Analysis.")
            
    return synthesis

def validate_exploratory_formatting(synthesis: PromptSynthesis) -> PromptSynthesis:
    """
    Prevents over-engineering verbosity on exploratory prompts.
    """
    if "exploratory" in synthesis.prompt_structure.reasoning_style.lower() or "socratic" in synthesis.prompt_structure.reasoning_style.lower():
        # Remove any hallucinated rigid constraints
        synthesis.prompt_structure.constraints = [c for c in synthesis.prompt_structure.constraints if "strict format" not in c.lower() and "must output json" not in c.lower()]
    return synthesis
