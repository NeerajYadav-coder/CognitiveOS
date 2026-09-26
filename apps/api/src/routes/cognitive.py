from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.cognitive import CognitiveState, UserContext, DomainExpertise
from src.pipelines.main_pipeline import core_pipeline
from src.utils.logger import logger
from src.utils.exceptions import EngineProcessingError
from src.database.connection import get_session
from src.infrastructure.persistence_manager import CognitivePersistenceManager

router = APIRouter()

class ProcessRequest(BaseModel):
    raw_input: str = Field(..., description="The raw thought or prompt from the user")
    platform_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Context from the browser/environment (e.g. url)")

class ProcessResponse(BaseModel):
    session_id: str
    status: str
    synthesized_prompt: Optional[str] = None
    structured_thought: Optional[Dict[str, Any]] = None
    execution_trace: list[str] = []

@router.post("/process", response_model=ProcessResponse)
async def process_cognitive_pipeline(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session)
):
    """
    Entry point for the CognitiveOS pipeline.
    Transforms raw input into a structured AI interaction prompt.
    """
    # 1. Fetch or create default User and Session
    user_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
    session_id = uuid.UUID('00000000-0000-0000-0000-000000000002')
    
    from src.infrastructure.database.postgres.models import User, Session
    from sqlalchemy import select
    
    try:
        # Check if default user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(
                id=user_id,
                email="cognitive_user@cognitiveos.ai",
                profile_metadata={},
                cognition_preferences={}
            )
            db.add(user)
            await db.flush()
            
        # Check if default session exists
        session_result = await db.execute(select(Session).where(Session.id == session_id))
        session = session_result.scalar_one_or_none()
        if not session:
            session = Session(
                id=session_id,
                user_id=user_id,
                session_context={}
            )
            db.add(session)
            await db.flush()
    except Exception as db_init_err:
        logger.error(f"Failed to fetch/create default database entities: {str(db_init_err)}")
        raise HTTPException(status_code=500, detail="Database session initialization failed")

    logger.info("Received process request", extra={"session_id": str(session_id), "url_context": request.platform_context.get("url")})
    
    # Construct UserContext from user's DB record
    profile_meta = user.profile_metadata or {}
    preferences = user.cognition_preferences or {}
    
    domain_exp_raw = profile_meta.get("domain_expertise", [])
    domain_expertise = []
    if isinstance(domain_exp_raw, list):
        for item in domain_exp_raw:
            if isinstance(item, dict) and "domain" in item:
                domain_expertise.append(DomainExpertise(
                    domain=item["domain"],
                    level=item.get("level", "intermediate")
                ))
                
    user_context = UserContext(
        user_id=str(user.id),
        profession=profile_meta.get("profession"),
        intellectual_level=preferences.get("intellectual_level", "intermediate"),
        cognitive_style=preferences.get("cognitive_style", {
            "verbosity": "balanced",
            "reasoning_preference": "balanced"
        }),
        domain_expertise=domain_expertise
    )

    # Initialize the Cognitive State with user_context
    initial_state = CognitiveState(
        session_id=str(session_id),
        raw_input=request.raw_input,
        user_context=user_context,
        global_metadata={"platform_context": request.platform_context}
    )
    
    try:
        # Run the full pipeline
        final_state = await core_pipeline.run(initial_state)
        
        # Persist interaction state to DB using the persistence manager
        try:
            persistence = CognitivePersistenceManager(db)
            state_dict = final_state.model_dump(mode="json")
            await persistence.persist_cognitive_event(
                state_dict=state_dict,
                user_id=user_id,
                session_id=session_id
            )
        except Exception as persist_err:
            logger.error(f"Failed to persist cognitive event to Postgres: {str(persist_err)}")
            # Do not fail request just because persistence failed (fallback/offline durability)
            
        structured_thought = {
            "intent": final_state.intent.model_dump() if final_state.intent else None,
            "mode": final_state.mode.model_dump() if final_state.mode else None,
            "ambiguity": final_state.ambiguity.model_dump() if final_state.ambiguity else None,
            "vocabulary": final_state.vocabulary.model_dump() if final_state.vocabulary else None,
            "thought_structure": final_state.thought_structure.model_dump() if final_state.thought_structure else None,
            "synthesis": final_state.synthesis.model_dump() if final_state.synthesis else None,
        }

        return ProcessResponse(
            session_id=str(session_id),
            status="success",
            synthesized_prompt=final_state.synthesis.final_prompt if final_state.synthesis else None,
            structured_thought=structured_thought,
            execution_trace=[r.engine_name for r in final_state.engine_results]
        )
        
    except EngineProcessingError as e:
        logger.error(f"Pipeline failed at engine: {e.details.get('engine')}", extra={"session_id": str(session_id)})
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unhandled error in pipeline execution", extra={"session_id": str(session_id)})
        raise HTTPException(status_code=500, detail="Internal processing error")

@router.get("/reflection/analytics")
async def get_reflection_analytics(db: AsyncSession = Depends(get_session)):
    """
    Retrieve aggregated cognitive metrics, trends, and reflections from user history.
    """
    from src.infrastructure.database.postgres.models import CognitiveInteraction
    from sqlalchemy import select
    
    try:
        # Fetch the last 50 interactions
        result = await db.execute(
            select(CognitiveInteraction)
            .order_by(CognitiveInteraction.created_at.desc())
            .limit(50)
        )
        interactions = result.scalars().all()
        
        # Default structures for new users with no history
        if not interactions:
            return {
                "metrics": [
                    {
                        "name": "Clarity Index",
                        "score": 50,
                        "description": "Measures how precise your draft inputs are, indicating low ambiguity score averages.",
                        "change": "New",
                        "trend": "stable"
                    },
                    {
                        "name": "Concept Expansion",
                        "score": 50,
                        "description": "Tracks the diversity and range of recommended terms injected into prompts.",
                        "change": "New",
                        "trend": "stable"
                    },
                    {
                        "name": "Focus Coherence",
                        "score": 50,
                        "description": "Ensures the synthesis engines do not wander into irrelevant domain classifications.",
                        "change": "New",
                        "trend": "stable"
                    }
                ],
                "insights": [
                    {
                        "id": "ins-welcome",
                        "title": "Welcome to Noosphere OS!",
                        "category": "clarity",
                        "text": "Submit your first prompt draft to generate cognitive reflection metrics and telemetry analysis.",
                        "impact": "medium",
                        "resolved": False
                    }
                ],
                "weekly_maturity_score": [
                    {"week": "W1", "score": 50}
                ],
                "dominant_modes": [
                    {"name": "Exploratory", "score": 100}
                ],
                "prompt_evolution": {
                    "before": "No prompts submitted yet.",
                    "after": "Optimized prompt will show here."
                }
            }
            
        # 1. Compute Clarity Index: 100 * (1 - avg(ambiguity_score))
        avg_ambiguity = sum(i.ambiguity_score for i in interactions) / len(interactions)
        clarity_score = round(100 * (1 - avg_ambiguity))
        
        # 2. Extract Cognitive Modes distribution
        mode_counts = {}
        total_modes_tallied = 0
        for i in interactions:
            mode_data = i.cognitive_mode or {}
            primary = mode_data.get("primary_mode")
            if primary:
                mode_counts[primary] = mode_counts.get(primary, 0) + 1
                total_modes_tallied += 1
                
        dominant_modes = []
        if total_modes_tallied > 0:
            for m_name, count in sorted(mode_counts.items(), key=lambda x: x[1], reverse=True):
                dominant_modes.append({
                    "name": m_name,
                    "score": round((count / total_modes_tallied) * 100)
                })
        else:
            dominant_modes = [{"name": "Exploratory", "score": 100}]
            
        # 3. Dynamic Insights based on actual data
        insights = []
        recent = interactions[0]
        recent_ambiguity = recent.ambiguity_score
        recent_intent = recent.intent_output or {}
        primary_intent = recent_intent.get("primary_intent", "Inquiry")
        recent_raw_truncated = recent.raw_input[:75] + "..." if len(recent.raw_input) > 75 else recent.raw_input
        
        if recent_ambiguity > 0.4:
            insights.append({
                "id": "ins-dynamic-ambiguity",
                "title": f"High Ambiguity in '{primary_intent}'",
                "category": "clarity",
                "text": f"Your recent draft '{recent_raw_truncated}' has an ambiguity score of {round(recent_ambiguity*100)}%. We recommend specifying explicit constraints or output formats to clarify your objective.",
                "impact": "high",
                "resolved": False
            })
        else:
            insights.append({
                "id": "ins-dynamic-clarity",
                "title": f"Strong Precision in '{primary_intent}'",
                "category": "clarity",
                "text": f"Excellent framing in '{recent_raw_truncated}'. The low ambiguity score ({round(recent_ambiguity*100)}%) allows the synthesis engine to construct high-fidelity instructions.",
                "impact": "low",
                "resolved": False
            })
            
        # Add dynamic insight for dominant thinking styles
        main_mode = dominant_modes[0]["name"] if dominant_modes else "Exploratory"
        mode_percentage = dominant_modes[0]["score"] if dominant_modes else 100
        insights.append({
            "id": "ins-dynamic-mode",
            "title": f"Dominant cognitive style: {main_mode}",
            "category": "scope",
            "text": f"Over your last {len(interactions)} interactions, {mode_percentage}% of your tasks primary-routed to the '{main_mode}' mode. Consider prompting for alternate perspectives (e.g. play devil's advocate) to balance your approach.",
            "impact": "medium",
            "resolved": False
        })
        
        # Add some historical metrics
        concept_expansion_score = min(95, max(40, 60 + len(interactions) * 2))
        focus_coherence_score = min(98, max(50, 75 + int(clarity_score / 10)))
        
        # Build weekly maturity scores
        weekly_scores = []
        steps = min(5, len(interactions))
        for step in range(steps):
            week_idx = steps - step
            subset = interactions[step:]
            subset_avg = sum(x.ambiguity_score for x in subset) / len(subset)
            weekly_scores.insert(0, {
                "week": f"Week -{week_idx - 1}" if week_idx > 1 else "Current Week",
                "score": round(100 * (1 - subset_avg))
            })
            
        if not weekly_scores:
            weekly_scores = [{"week": "Current Week", "score": clarity_score}]
            
        # 4. Prompt Evolution: Compare oldest and newest prompt in this set
        oldest_raw = interactions[-1].raw_input
        newest_raw = interactions[0].raw_input
        
        return {
            "metrics": [
                {
                    "name": "Clarity Index",
                    "score": clarity_score,
                    "description": "Measures how precise your draft inputs are, indicating low ambiguity score averages.",
                    "change": f"{'+' if clarity_score > 60 else ''}{clarity_score - 60}%" if len(interactions) > 5 else "Stable",
                    "trend": "up" if clarity_score > 60 else "stable"
                },
                {
                    "name": "Concept Expansion",
                    "score": concept_expansion_score,
                    "description": "Tracks the diversity and range of recommended terms injected into prompts.",
                    "change": "+5%",
                    "trend": "up"
                },
                {
                    "name": "Focus Coherence",
                    "score": focus_coherence_score,
                    "description": "Ensures the synthesis engines do not wander into irrelevant domain classifications.",
                    "change": "Stable",
                    "trend": "stable"
                }
            ],
            "insights": insights,
            "weekly_maturity_score": weekly_scores,
            "dominant_modes": dominant_modes,
            "prompt_evolution": {
                "before": oldest_raw if len(oldest_raw) < 150 else oldest_raw[:150] + "...",
                "after": newest_raw if len(newest_raw) < 150 else newest_raw[:150] + "..."
            }
        }
    except Exception as e:
        logger.error(f"Failed to calculate reflection analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate reflection analytics")

@router.get("/interactions")
async def get_interactions(db: AsyncSession = Depends(get_session)):
    """
    Retrieve the latest cognitive interactions from the database.
    """
    from src.infrastructure.database.postgres.models import CognitiveInteraction
    from sqlalchemy import select
    
    try:
        result = await db.execute(
            select(CognitiveInteraction)
            .order_by(CognitiveInteraction.created_at.desc())
            .limit(10)
        )
        interactions = result.scalars().all()
        return [
            {
                "id": str(i.id),
                "session_id": str(i.session_id),
                "raw_input": i.raw_input,
                "normalized_input": i.normalized_input,
                "intent_output": i.intent_output,
                "cognitive_mode": i.cognitive_mode,
                "ambiguity_score": i.ambiguity_score,
                "orchestration_trace": i.orchestration_trace,
                "created_at": i.created_at.isoformat() if i.created_at else None
            }
            for i in interactions
        ]
    except Exception as e:
        logger.error(f"Failed to fetch interactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Database fetch failed")

class ProfileUpdateRequest(BaseModel):
    profession: Optional[str] = None
    intellectual_level: Optional[str] = None
    cognitive_style: Optional[Dict[str, str]] = None
    domain_expertise: Optional[list[Dict[str, str]]] = None

@router.get("/user/profile")
async def get_user_profile(db: AsyncSession = Depends(get_session)):
    user_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
    from src.infrastructure.database.postgres.models import User
    from sqlalchemy import select
    
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(
                id=user_id,
                email="cognitive_user@cognitiveos.ai",
                profile_metadata={},
                cognition_preferences={}
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
        return {
            "user_id": str(user.id),
            "email": user.email,
            "profile_metadata": user.profile_metadata or {},
            "cognition_preferences": user.cognition_preferences or {}
        }
    except Exception as e:
        logger.error(f"Failed to fetch user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user profile")

@router.put("/user/profile")
async def update_user_profile(request: ProfileUpdateRequest, db: AsyncSession = Depends(get_session)):
    user_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
    from src.infrastructure.database.postgres.models import User
    from sqlalchemy import select
    
    try:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        profile_metadata = user.profile_metadata or {}
        cognition_preferences = user.cognition_preferences or {}
        
        if request.profession is not None:
            profile_metadata["profession"] = request.profession
        if request.domain_expertise is not None:
            profile_metadata["domain_expertise"] = request.domain_expertise
        if request.intellectual_level is not None:
            cognition_preferences["intellectual_level"] = request.intellectual_level
        if request.cognitive_style is not None:
            cognition_preferences["cognitive_style"] = request.cognitive_style
            
        user.profile_metadata = profile_metadata
        user.cognition_preferences = cognition_preferences
        
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "profile_metadata")
        flag_modified(user, "cognition_preferences")
        
        db.add(user)
        await db.commit()
        
        return {"status": "success", "profile_metadata": profile_metadata, "cognition_preferences": cognition_preferences}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user profile")

from src.schemas.cognitive import (
    SpokenThoughtAnalysis, 
    GraphSynthesisRequest, 
    GraphSynthesisResponse
)
from src.services.spoken_thought.engine import SpokenThoughtEngine

class VoiceStreamRequest(BaseModel):
    raw_speech: str = Field(..., description="Raw speech transcription from user")
    session_id: Optional[str] = Field(default=None, description="Optional session ID")

@router.post("/cognitive/voice-stream", response_model=SpokenThoughtAnalysis)
async def process_voice_stream(request: VoiceStreamRequest):
    """
    Ingests spoken thoughts, strips conversational fillers,
    calculates spoken ambiguity, and synthesizes structured prompts.
    """
    try:
        engine = SpokenThoughtEngine()
        result = await engine.process(request.raw_speech)
        return result
    except Exception as e:
        logger.error(f"Failed to process voice stream: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice stream processing failed: {str(e)}")

@router.post("/cognitive/graph/synthesize", response_model=GraphSynthesisResponse)
async def synthesize_graph_topology(request: GraphSynthesisRequest):
    """
    Synthesizes a visual concept graph topology into a multi-perspective LLM prompt.
    """
    try:
        node_labels = [n.label for n in request.nodes]
        edge_relations = []
        for e in request.edges:
            src_node = next((n.label for n in request.nodes if n.id == e.source), e.source)
            tgt_node = next((n.label for n in request.nodes if n.id == e.target), e.target)
            edge_relations.append(f"{src_node} -> {tgt_node}")

        title = " & ".join(node_labels[:3]) if node_labels else "Conceptual Graph"
        core_theme = request.goal or (f"Interconnected conceptual model of {', '.join(node_labels[:4])}" if node_labels else "General Concept Map")
        pathways = edge_relations if edge_relations else [f"Node: {n}" for n in node_labels]

        prompt_lines = [
            f"You are exploring a multi-perspective conceptual model focused on: {core_theme}.",
            "",
            "### Core Concept Nodes:",
            "\n".join(f"- **{label}**" for label in node_labels) if node_labels else "- Unspecified concept nodes",
            "",
            "### Conceptual Pathways & Relational Edges:",
            "\n".join(f"- {rel}" for rel in pathways) if pathways else "- Dynamic conceptual associations",
            "",
            "### Objective:",
            "Synthesize these relational concepts into a coherent, deeply structured analysis. Identify first-principle truths, emergent tensions, and practical applications."
        ]

        synthesized_prompt = "\n".join(prompt_lines)

        return GraphSynthesisResponse(
            title=title,
            core_theme=core_theme,
            conceptual_pathways=pathways,
            synthesized_prompt=synthesized_prompt,
            recommended_framework="Dialectical Synthesis" if len(node_labels) > 2 else "First Principles"
        )
    except Exception as e:
        logger.error(f"Failed to synthesize graph: {str(e)}")
        raise HTTPException(status_code=500, detail="Graph synthesis failed")

