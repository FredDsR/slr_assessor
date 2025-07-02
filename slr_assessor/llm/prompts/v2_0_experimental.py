"""Experimental prompt version with different focus areas."""

from ..prompt_manager import PromptVersion

QA_QUESTIONS_V2_0 = {
    "QA1": "Does the abstract examine cultural considerations and cultural sensitivity in AI technology adoption within traditional communities?",
    "QA2": "Does the abstract investigate community participation, stakeholder engagement, or participatory approaches in AI-community integration processes?",
    "QA3": "Does the abstract address sustainability, long-term impacts, or enduring effects of AI adoption in traditional settings?",
    "QA4": "Does the abstract provide measurable outcomes, evaluation metrics, or success indicators for AI-community integration effectiveness?",
}

ASSESSMENT_PROMPT_TEMPLATE_V2_0 = """You are conducting a systematic literature review focusing on cultural and participatory aspects of AI integration in traditional communities.

Evaluate this abstract against these research questions:

1. {qa1_question}
2. {qa2_question}
3. {qa3_question}
4. {qa4_question}

Abstract:
{abstract_text}

Assessment Instructions:
- Focus on cultural sensitivity, community participation, and sustainable integration
- Consider both explicit mentions and implied approaches
- Score based on relevance to participatory AI implementation
- Emphasize community-centered and culturally-aware AI development

Provide scores (0.0-1.0) and reasoning for each question.

Respond in valid JSON format:
{{
  "assessments": [
    {{"qa_id": "QA1", "question": "{qa1_question}", "score": 0.0, "reason": "Brief explanation"}},
    {{"qa_id": "QA2", "question": "{qa2_question}", "score": 0.0, "reason": "Brief explanation"}},
    {{"qa_id": "QA3", "question": "{qa3_question}", "score": 0.0, "reason": "Brief explanation"}},
    {{"qa_id": "QA4", "question": "{qa4_question}", "score": 0.0, "reason": "Brief explanation"}}
  ],
  "overall_summary": "A brief overall summary of the abstract's quality and relevance."
}}"""

PROMPT_V2_0 = PromptVersion(
    version="v2.0",
    name="Cultural-Participatory Focus",
    description="Experimental prompt focusing on cultural aspects and community participation",
    qa_questions=QA_QUESTIONS_V2_0,
    template=ASSESSMENT_PROMPT_TEMPLATE_V2_0,
    created_date="2025-06-01",
    is_active=True
)
