"""LaTeX section extraction and replacement utilities using %%TAG%% markers."""

import re

_TAG_BEGIN = re.compile(r"^%\s*%%(\w+)_BEGIN%%\s*$")
_TAG_END = re.compile(r"^%\s*%%(\w+)_END%%\s*$")


def _find_all_tags(lines: list[str]) -> dict[str, tuple[int, int]]:
    """Scan for %%TAG_BEGIN%% / %%TAG_END%% markers, return {name: (begin, end)}."""
    opens: dict[str, int] = {}
    ranges: dict[str, tuple[int, int]] = {}

    for i, line in enumerate(lines):
        m = _TAG_BEGIN.match(line.strip())
        if m:
            opens[m.group(1)] = i
            continue
        m = _TAG_END.match(line.strip())
        if m:
            name = m.group(1)
            if name in opens:
                ranges[name] = (opens[name], i)

    return ranges


def extract_section_ranges(lines: list[str]) -> dict:
    """Find summary and skills line ranges using %%TAG%% markers."""
    ranges = _find_all_tags(lines)

    if "SUMMARY" not in ranges:
        raise ValueError("Could not locate %%SUMMARY_BEGIN/END%% tags in template")
    if "SKILLS" not in ranges:
        raise ValueError("Could not locate %%SKILLS_BEGIN/END%% tags in template")

    return {
        "summary": ranges["SUMMARY"],
        "skills": ranges["SKILLS"],
    }


def extract_sections(lines: list[str], ranges: dict) -> dict:
    """Extract Summary and Skills text from template lines."""
    s_start, s_end = ranges["summary"]
    k_start, k_end = ranges["skills"]
    return {
        "summary": "".join(lines[s_start + 1 : s_end]),
        "skills": "".join(lines[k_start + 1 : k_end]),
    }


def extract_experience(lines: list[str]) -> str:
    """Extract the Work Experience section for LLM context."""
    ranges = _find_all_tags(lines)
    if "EXPERIENCE" not in ranges:
        return ""
    start, end = ranges["EXPERIENCE"]
    return "".join(lines[start + 1 : end])


def parse_known_skills(skills_text: str) -> set[str]:
    """Parse original skills section into a set of lowercase skill tokens."""
    tokens = set()
    for line in skills_text.splitlines():
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
            if cleaned:
                tokens.add(cleaned.lower())
    return tokens


def replace_sections(
    lines: list[str], ranges: dict, new_summary: str, new_skills: str
) -> list[str]:
    """Replace summary and skills sections. Returns new list of lines."""
    result = lines.copy()

    s_start, s_end = ranges["skills"]
    replacement = new_skills.splitlines(keepends=True)
    result[s_start + 1 : s_end] = replacement
    if new_skills and not new_skills.endswith("\n"):
        result.insert(s_start + 1 + len(replacement), "\n")

    s_start, s_end = ranges["summary"]
    replacement = new_summary.splitlines(keepends=True)
    result[s_start + 1 : s_end] = replacement
    if new_summary and not new_summary.endswith("\n"):
        result.insert(s_start + 1 + len(replacement), "\n")

    return result
