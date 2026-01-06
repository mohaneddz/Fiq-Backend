"""
System prompts for Relapse service.
"""

PREDICTION_DISCLAIMER = """
IMPORTANT: This relapse prediction is based on behavioral patterns and should be used 
as a supportive tool only. It is NOT a substitute for professional medical advice, 
diagnosis, or treatment. Always consult with qualified healthcare providers for 
personalized recovery guidance.

The prediction is intended to:
- Help identify potential risk patterns
- Support proactive intervention planning
- Encourage engagement with support systems
- Facilitate data-driven recovery discussions

If you or someone you know is in crisis, please contact:
- SAMHSA National Helpline: 1-800-662-4357
- Crisis Text Line: Text HOME to 741741
- National Suicide Prevention Lifeline: 988
"""

FEATURE_EXPLANATIONS = {
    "days_clean": "Number of days since last relapse - longer periods indicate stability",
    "craving_trend": "Average craving intensity over the past week - higher values indicate risk",
    "sleep_deviation": "Irregularity in sleep patterns - higher deviation suggests stress",
    "trigger_count": "Number of trigger exposures in the past week - more triggers increase risk",
    "support_sessions": "Number of therapy/support meetings attended - more is protective",
    "medication_adherence": "Percentage of prescribed medication taken correctly - higher is better"
}
