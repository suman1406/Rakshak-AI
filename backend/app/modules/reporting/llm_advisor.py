"""
LLM Advisor Service - Generates AI-powered advisory reports for crop disease diagnosis.
Uses Groq's LLM API to provide actionable advice based on Bayesian diagnosis results.
"""

import json
import logging
from typing import Any

from groq import AsyncGroq
from groq.types.chat import ChatCompletion

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_prompt(
    crop: str,
    disease: str,
    confidence: float,
    confidence_band: str,
    severity_level: int,
    affected_plant_estimate: float,
    supporting_frames: int,
) -> str:
    """Build a structured prompt for the LLM."""
    severity_descriptions = {
        0: "Minimal - No visible symptoms or very minor issues",
        1: "Low - Slight symptoms visible, limited impact on plant health",
        2: "Medium - Moderate symptoms, noticeable impact on plant health",
        3: "High - Severe symptoms, significant damage to plant",
    }

    prompt = f"""You are an agricultural expert system providing advisory reports for crop disease diagnosis.
Generate a concise, actionable advisory report based on the following diagnosis information.

DIAGNOSIS INFORMATION:
- Crop Type: {crop}
- Diagnosed Disease: {disease}
- Bayesian Confidence Score: {confidence:.2%}
- Confidence Band: {confidence_band.upper()}
- Severity Level: {severity_level} ({severity_descriptions.get(severity_level, "Unknown")})
- Estimated Affected Plants: {affected_plant_estimate:.1f}%
- Supporting Evidence Frames: {supporting_frames}

OUTPUT FORMAT (JSON only, no other text):
{{
    "headline": "A brief, compelling headline summarizing the diagnosis (max 100 characters)",
    "explanation": "A clear explanation of what the diagnosis means for the farmer, including the disease name and why it was identified (max 300 characters)",
    "action_items": [
        "Specific actionable step 1",
        "Specific actionable step 2",
        "Specific actionable step 3"
    ],
    "safety_disclaimer": "AI estimate, not a confirmed diagnosis. Consult an agronomist."
}}

REQUIREMENTS:
1. Always include the safety disclaimer
2. Never provide lethal chemical recipes or dosages
3. Provide 3-5 actionable steps that the farmer can take
4. Be specific to the crop and disease when giving advice
5. Keep explanations clear and concise
6. Consider the severity level when generating action items

Return ONLY valid JSON, no markdown formatting, no explanations."""
    return prompt


async def generate_advisory_report(
    crop: str,
    disease: str,
    confidence: float,
    confidence_band: str,
    severity_level: int,
    affected_plant_estimate: float,
    supporting_frames: int,
) -> dict[str, Any] | None:
    """
    Generate an AI-powered advisory report using Groq LLM.
    
    Args:
        crop: The type of crop being diagnosed
        disease: The diagnosed disease name
        confidence: Bayesian confidence score (0.0 to 1.0)
        confidence_band: Confidence band category (high/medium/low)
        severity_level: Severity level from 0-3
        affected_plant_estimate: Estimated percentage of affected plants
        supporting_frames: Number of evidence frames supporting the diagnosis
    
    Returns:
        Dictionary with headline, explanation, action_items, and safety_disclaimer,
        or None if the LLM call fails
    """
    # Check if Groq API key is configured
    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not configured, cannot generate LLM advisory report")
        return None

    try:
        client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        
        prompt = _build_prompt(
            crop=crop,
            disease=disease,
            confidence=confidence,
            confidence_band=confidence_band,
            severity_level=severity_level,
            affected_plant_estimate=affected_plant_estimate,
            supporting_frames=supporting_frames,
        )

        response: ChatCompletion = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an agricultural expert system. Generate concise, actionable advisory reports in JSON format only.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.3,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        
        if not content:
            logger.warning("Empty response from Groq LLM")
            return None

        # Parse the JSON response
        result = json.loads(content)
        
        # Validate required fields
        required_fields = ["headline", "explanation", "action_items", "safety_disclaimer"]
        for field in required_fields:
            if field not in result:
                logger.error(f"Missing required field in LLM response: {field}")
                return None

        # Ensure action_items is a list
        if isinstance(result["action_items"], str):
            result["action_items"] = [result["action_items"]]

        logger.info(f"Successfully generated advisory report for {crop}/{disease}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Error generating advisory report: {e}")
        return None