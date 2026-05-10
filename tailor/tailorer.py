"""Core resume tailoring logic."""

import json
import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from .latex_utils import (
    extract_experience,
    extract_section_ranges,
    extract_sections,
    parse_known_skills,
    replace_sections,
)
from .prompts import SYSTEM_PROMPT, build_user_message

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "glm-4.7-flash"


def _create_client() -> OpenAI:
    load_dotenv()
    api_key = os.environ.get("ZAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "ZAI_API_KEY not set. Create a .env file (see .env.example) "
            "or export the variable."
        )
    return OpenAI(api_key=api_key, base_url="https://api.z.ai/api/paas/v4/")


def _call_llm(
    client: OpenAI,
    model: str,
    user_message: str,
) -> str:
    logger.info("Calling %s via Z.AI API...", model)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content


def _parse_llm_response(raw: str) -> dict:
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if not json_match:
        raise ValueError(f"LLM response does not contain JSON:\n{raw}")
    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM JSON response: {e}") from e


def _validate_skills(new_skills: str, known_skills: set[str]) -> None:
    for line in new_skills.splitlines():
        if r"\textbf{" not in line:
            continue
        colon_pos = line.find("}")
        if colon_pos == -1:
            continue
        content = line[colon_pos + 1:].strip()
        if content.startswith(":"):
            content = content[1:].strip()
        for token in content.split(","):
            cleaned = token.strip().rstrip("\\[2pt]").strip()
            if not cleaned:
                continue
            if cleaned.lower() not in known_skills:
                logger.warning("Potentially fabricated skill: %s", cleaned)


def _fix_latex(text: str) -> str:
    """Fix common LLM LaTeX formatting errors."""
    # Fix "\ " (backslash-space) used as line break -> \\ + newline
    text = re.sub(r"\\ (?=[A-Za-z])", r"\\\\\n", text)
    # Fix single backslash before uppercase words (e.g. \Designed -> \\ + newline)
    text = re.sub(r"\\([A-Z][a-zA-Z])", r"\\\\\n\1", text)
    # Fix \[2pt] -> \\[2pt] + newline
    text = re.sub(r"(?<!\\)\\\[2pt\]", r"\\\\[2pt]\n", text)
    return text


def tailor_resume(
    job_description_path: str,
    template_path: str = "yury_bely_cv.tex",
    output_path: str | None = None,
    model: str = DEFAULT_MODEL,
    build: bool = False,
    dry_run: bool = False,
) -> Path:
    jd_text = Path(job_description_path).read_text().strip()
    if not jd_text:
        raise SystemExit(f"Job description file is empty: {job_description_path}")

    template = Path(template_path)
    if not template.exists():
        raise SystemExit(f"Template not found: {template_path}")

    lines = template.read_text().splitlines(keepends=True)
    ranges = extract_section_ranges(lines)
    sections = extract_sections(lines, ranges)
    experience = extract_experience(lines)
    known_skills = parse_known_skills(sections["skills"])

    client = _create_client()
    user_msg = build_user_message(
        job_description=jd_text,
        current_summary=sections["summary"],
        current_skills=sections["skills"],
        experience=experience,
    )

    raw = _call_llm(client, model, user_msg)
    logger.debug("Raw LLM response:\n%s", raw)

    parsed = _parse_llm_response(raw)
    new_summary = _fix_latex(parsed["summary"])
    new_skills = _fix_latex(parsed["skills"])

    _validate_skills(new_skills, known_skills)

    if dry_run:
        print("=== TAILORED SUMMARY ===")
        print(new_summary)
        print("\n=== TAILORED SKILLS ===")
        print(new_skills)
        return Path("")

    new_lines = replace_sections(lines, ranges, new_summary, new_skills)
    result_text = "".join(new_lines)

    if output_path is None:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output/yury_bely_cv_tailored_{timestamp}.tex"

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result_text)
    logger.info("Tailored resume saved to %s", out)

    if build:
        import subprocess

        logger.info("Building PDF...")
        subprocess.run(["bash", "build.sh", str(out), str(out.parent)], check=True)

    return out
