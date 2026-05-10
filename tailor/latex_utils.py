"""LaTeX section extraction and replacement utilities."""


def extract_section_ranges(lines: list[str]) -> dict:
    """Find summary and skills line ranges by scanning for anchor markers."""
    ranges = {}

    for i, line in enumerate(lines):
        if line.strip() == r"\noindent\color{graytext}\small" and i < 100:
            for j in range(i + 1, min(i + 10, len(lines))):
                if lines[j].strip().startswith("%"):
                    ranges["summary"] = (i, j)
                    break
            break

    for i, line in enumerate(lines):
        if r"\heading{Technical Skills}" in line:
            for j in range(i + 1, min(i + 20, len(lines))):
                if lines[j].strip() == r"\end{document}":
                    ranges["skills"] = (i + 1, j)
                    break
            break

    if "summary" not in ranges:
        raise ValueError("Could not locate Summary section in template")
    if "skills" not in ranges:
        raise ValueError("Could not locate Technical Skills section in template")

    return ranges


def extract_sections(lines: list[str], ranges: dict) -> dict:
    """Extract Summary and Skills text from template lines."""
    s_start, s_end = ranges["summary"]
    k_start, k_end = ranges["skills"]
    return {
        "summary": "".join(lines[s_start:s_end]),
        "skills": "".join(lines[k_start:k_end]),
    }


def extract_experience(lines: list[str]) -> str:
    """Extract the Work Experience section for LLM context."""
    start = end = None
    for i, line in enumerate(lines):
        if r"\heading{Work Experience}" in line:
            start = i
        if start is not None and "% ── Education" in line:
            end = i
            break
    if start is None or end is None:
        return ""
    return "".join(lines[start:end])


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
    result[s_start:s_end] = new_skills.splitlines(keepends=True)
    if not new_skills.endswith("\n"):
        result.insert(s_start + len(new_skills.splitlines()), "\n")

    s_start, s_end = ranges["summary"]
    result[s_start:s_end] = new_summary.splitlines(keepends=True)
    if not new_summary.endswith("\n"):
        result.insert(s_start + len(new_summary.splitlines()), "\n")

    return result
