"""Default prompt version - matches original implementation."""

from ..prompt_manager import PromptVersion

QA_QUESTIONS_V1_0 = {
    "QA1": "Does the abstract clearly present the study's objective, research question, or central focus?",
    "QA2": "Does the abstract provide any indication of a practical application or an empirical result?",
    "QA3": "Does the abstract contextualize the challenge faced by the traditional community or by the application of AI?",
    "QA4": "Does the abstract directly address the integration of AI with traditional communities/knowledge?",
}

ASSESSMENT_PROMPT_TEMPLATE_V1_0 = """You are a meticulous academic researcher tasked with conducting a quality assessment of a research paper based solely on its abstract. Your evaluation must strictly follow the provided Quality Assurance (QA) criteria.

**Instructions:**
1. Read the abstract below carefully.
2. For each of the four QA questions, provide a score and a brief, one-sentence reason for that score.
3. The score for each question MUST be one of these three values: **1** (satisfies), **0.5** (partially satisfies), or **0** (does not satisfy).
4. Your entire response must be a single, valid JSON object, with no text before or after it.

**Abstract to Evaluate:**
\"\"\"
{abstract_text}
\"\"\"

**JSON Output Structure:**
{{
  "assessments": [
    {{
      "qa_id": "QA1",
      "question": "{qa1_question}",
      "score": <0, 0.5, or 1>,
      "reason": "..."
    }},
    {{
      "qa_id": "QA2",
      "question": "{qa2_question}",
      "score": <0, 0.5, or 1>,
      "reason": "..."
    }},
    {{
      "qa_id": "QA3",
      "question": "{qa3_question}",
      "score": <0, 0.5, or 1>,
      "reason": "..."
    }},
    {{
      "qa_id": "QA4",
      "question": "{qa4_question}",
      "score": <0, 0.5, or 1>,
      "reason": "..."
    }}
  ],
  "overall_summary": "A brief overall summary of the abstract's quality and relevance."
}}"""

PROMPT_V1_0 = PromptVersion(
    version="v1.0",
    name="Default SLR Assessment",
    description="Original prompt for AI-traditional community integration studies",
    qa_questions=QA_QUESTIONS_V1_0,
    template=ASSESSMENT_PROMPT_TEMPLATE_V1_0,
    created_date="2025-01-01",
    is_active=True
)
