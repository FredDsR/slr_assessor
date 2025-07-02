"""Built-in prompt versions for SLR assessment."""

from .v1_0_default import PROMPT_V1_0
from .v1_1_enhanced import PROMPT_V1_1
from .v1_2_enhanced_questions import PROMPT_V1_2
from .v2_0_experimental import PROMPT_V2_0

# Registry of all built-in prompt versions
BUILT_IN_PROMPTS = {
    "v1.0": PROMPT_V1_0,
    "v1.1": PROMPT_V1_1,
    "v1.2": PROMPT_V1_2,
    "v2.0": PROMPT_V2_0,
}

__all__ = ["BUILT_IN_PROMPTS", "PROMPT_V1_0", "PROMPT_V1_1", "PROMPT_V1_2", "PROMPT_V2_0"]
