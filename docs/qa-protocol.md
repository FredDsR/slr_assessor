# Quality Assurance Protocol

This document defines the standardized QA protocol used by the SLR Assessor for evaluating papers in systematic literature reviews.

## QA Questions

The system evaluates papers based on four core quality assurance questions:

### QA1: Study Objective Clarity
**Question:** Does the abstract clearly present the study's objective, research question, or central focus?

**Evaluation Criteria:**
- **Score 1**: Abstract explicitly states research objectives, hypotheses, or research questions
- **Score 0.5**: Abstract implies or partially mentions study objectives
- **Score 0**: Abstract lacks clear indication of study objectives or research focus

**Examples:**
- Score 1: "This study aims to investigate the effectiveness of AI-powered diagnostic tools..."
- Score 0.5: "We explore the potential of machine learning in medical diagnosis..."
- Score 0: "Artificial intelligence is becoming increasingly important in healthcare..."

### QA2: Practical Application Evidence
**Question:** Does the abstract provide any indication of a practical application or an empirical result?

**Evaluation Criteria:**
- **Score 1**: Clear mention of practical applications, empirical results, or real-world implementations
- **Score 0.5**: Suggests practical relevance or mentions preliminary results
- **Score 0**: Purely theoretical or conceptual with no practical application mentioned

**Examples:**
- Score 1: "Results show 95% accuracy in clinical trials with 1000 patients..."
- Score 0.5: "Preliminary results suggest potential for clinical application..."
- Score 0: "We propose a theoretical framework for understanding AI in healthcare..."

### QA3: Challenge Contextualization
**Question:** Does the abstract contextualize the challenge faced by the traditional community or by the application of AI?

**Evaluation Criteria:**
- **Score 1**: Clearly identifies and contextualizes specific challenges or problems
- **Score 0.5**: Mentions challenges but with limited context or detail
- **Score 0**: No clear identification of challenges or problems addressed

**Examples:**
- Score 1: "Traditional diagnostic methods suffer from high error rates and time constraints..."
- Score 0.5: "Current approaches face several limitations..."
- Score 0: "AI offers new possibilities for healthcare improvement..."

### QA4: AI-Traditional Integration
**Question:** Does the abstract directly address the integration of AI with traditional communities/knowledge?

**Evaluation Criteria:**
- **Score 1**: Explicitly discusses integration, collaboration, or bridging AI with traditional approaches
- **Score 0.5**: Implies or suggests integration between AI and traditional methods
- **Score 0**: No clear indication of integration or relationship between AI and traditional approaches

**Examples:**
- Score 1: "Our approach combines traditional clinical expertise with AI-powered analysis..."
- Score 0.5: "The system supports healthcare professionals in decision-making..."
- Score 0: "We developed an AI system for medical diagnosis..."

## Scoring System

### Individual Scores
Each QA question receives a score of:
- **0**: Does not meet criteria
- **0.5**: Partially meets criteria
- **1**: Fully meets criteria

### Total Score Calculation
Total score = QA1 + QA2 + QA3 + QA4 (Range: 0-4)

### Decision Thresholds

Based on the total score, papers are categorized as:

- **Include**: total_score ≥ 2.5
  - Strong evidence of meeting multiple QA criteria
  - Recommended for full review
  
- **Conditional Review**: 1.5 ≤ total_score < 2.5
  - Moderate evidence of meeting QA criteria
  - Requires human review for final decision
  - May need additional evaluation
  
- **Exclude**: total_score < 1.5
  - Insufficient evidence of meeting QA criteria
  - Not recommended for inclusion

## Implementation Guidelines

### For LLM Assessment
1. **Consistency**: LLMs are prompted to apply these criteria uniformly
2. **Reasoning**: Each score must be accompanied by clear reasoning
3. **Structured Output**: Results follow standardized JSON format
4. **Validation**: Scores are validated against allowed values (0, 0.5, 1)

### For Human Assessment
1. **Training**: Reviewers should be trained on these criteria
2. **Calibration**: Use sample papers to ensure consistent application
3. **Documentation**: Provide clear reasoning for each score
4. **Double-checking**: Consider inter-rater reliability measures

## Quality Control Measures

### Automated Validation
- Score range validation (0, 0.5, 1 only)
- Required reasoning for each score
- Structural integrity of responses
- Consistency checks across assessments

### Human Oversight
- Spot-checking of LLM assessments
- Review of edge cases (scores near thresholds)
- Validation of reasoning quality
- Calibration with human assessments

## Adaptation Guidelines

### Customizing for Different Domains
While the core QA framework is designed for AI-traditional community integration studies, it can be adapted:

1. **Question Modification**: Adjust QA questions for specific research domains
2. **Threshold Adjustment**: Modify decision thresholds based on review requirements
3. **Scoring Refinement**: Add sub-criteria for more nuanced evaluation
4. **Domain-Specific Examples**: Provide relevant examples for different fields

### Maintaining Consistency
When adapting the protocol:
- Document all modifications clearly
- Provide updated training materials
- Validate new criteria with sample papers
- Maintain backwards compatibility where possible

## Reporting and Documentation

### Assessment Records
Each assessment should include:
- Paper identifier and metadata
- Individual QA scores and reasoning
- Total score and decision
- Assessor information (LLM model or human reviewer)
- Timestamp and session information

### Quality Metrics
Track and report:
- Inter-rater reliability (Cohen's Kappa)
- Score distributions
- Decision consistency
- Assessment completion rates
- Error rates and types

This protocol ensures standardized, traceable, and reliable paper screening for systematic literature reviews.
