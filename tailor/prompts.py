"""LLM prompt templates for resume tailoring."""

SYSTEM_PROMPT = """\
You are a professional resume writer specializing in ATS-optimized \
software engineering resumes.
Your task is to tailor ONLY the Summary and Technical Skills sections \
of a LaTeX resume to match a specific job description.

CRITICAL RULES:
1. You MUST NOT invent, fabricate, or add any skill, technology, or \
experience that is not already present in the candidate's resume.
2. You may only REORDER, RE-PHRASE, and RE-EMPHASIZE existing content \
to better match the job description.
3. The Summary must remain 2-3 sentences of factual content from the resume.
4. Skills categories (Core Expertise, Languages, Frameworks and Libraries, \
Databases, Platforms, Tools, AI/ML) must ALL be preserved.
5. Individual items within each category may be reordered but not removed or added.
6. LaTeX formatting commands must be preserved EXACTLY as in the original:
   - Use exactly TWO backslashes for line breaks: \\\\
   - Use exactly \\\\[2pt] at the end of each skills line
   - Never use a single backslash before text words (e.g. wrong: \\Designed, \\Built)
7. Do not add any new \\textbf category labels.
"""


def build_user_message(
    job_description: str,
    current_summary: str,
    current_skills: str,
    experience: str,
) -> str:
    return f"""\
<job_description>
{job_description}
</job_description>

<current_summary>
{current_summary}
</current_summary>

<current_skills>
{current_skills}
</current_skills>

<full_experience>
{experience}
</full_experience>

Analyze the job description and produce two outputs:

1. TAILORED SUMMARY (2-3 sentences in LaTeX format):
   - Lead with the most relevant aspect of the candidate's experience for this role
   - Emphasize technologies and domains that overlap with the job requirements
   - Keep all factual claims verifiable from the experience section
   - Maintain the \\noindent\\color{{graytext}}\\small prefix on the first line
   - Use \\\\ for line breaks between sentences

2. TAILORED SKILLS (same LaTeX format as current, all 7 categories):
   - Within each category, move skills that match the job description to the front
   - Preserve the \\textbf{{Category Name:}} format exactly
   - Preserve \\\\[2pt] line endings exactly
   - The order of categories themselves may be changed to match job priority

Return your response as a JSON object with exactly two keys:
{{
  "summary": "<the complete LaTeX lines for the summary>",
  "skills": "<the complete LaTeX lines for the skills section>"
}}\
"""
