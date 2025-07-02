"""Enhanced prompt version with improved clarity and examples."""

from ..prompt_manager import PromptVersion

QA_QUESTIONS_V1_1 = {
    "QA1": "Does the abstract clearly present the study's objective, research question, or central focus with specific details?",
    "QA2": "Does the abstract provide clear indication of practical applications, empirical results, or real-world implementations?",
    "QA3": "Does the abstract contextualize specific challenges, barriers, or problems faced by traditional communities or AI applications?",
    "QA4": "Does the abstract directly address methodologies, frameworks, or approaches for integrating AI with traditional communities/knowledge?",
}

ASSESSMENT_PROMPT_TEMPLATE_V1_1 = """You are an expert reviewer conducting a systematic literature review on AI integration with traditional community structures.

Please assess the following abstract based on these specific criteria:

1. {qa1_question}
2. {qa2_question}
3. {qa3_question}
4. {qa4_question}

Abstract to assess:
{abstract_text}

Scoring Guidelines:
- 1.0: Abstract clearly and directly addresses the question with specific details
- 0.5: Abstract addresses the question with some detail but aspects may be unclear
- 0.0: Abstract does not address the question or mentions it only in passing

For each question, provide:
- A score from 0.0 to 1.0 based on the guidelines above
- A concise reason explaining your scoring decision

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

PROMPT_V1_1 = PromptVersion(
    version="v1.1",
    name="Enhanced SLR Assessment",
    description="Improved prompt with clearer criteria and scoring guidelines",
    qa_questions=QA_QUESTIONS_V1_1,
    template=ASSESSMENT_PROMPT_TEMPLATE_V1_1,
    created_date="2025-03-01",
    is_active=True
)
