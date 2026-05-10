# CV

LaTeX-based resume with automatic tailoring for job applications.

## Prerequisites

- Python 3.11+ with `.venv`
- Docker (for PDF generation)
- Z.AI API key ([open.z.ai](https://open.z.ai))

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` file with your API key (see `.env.example`):

```
ZAI_API_KEY=your-key-here
```

## Generating PDF from LaTeX

Build PDF from any `.tex` file using Docker:

```bash
bash build.sh                                         # builds yury_bely_cv.tex to output/
bash build.sh output/my_resume.tex                    # builds specific file to output/
bash build.sh output/my_resume.tex manual             # builds specific file to manual/
```

Output is saved to `output/` with a timestamp in the filename.

## Tailoring Resume for a Job Application

### 1. Prepare a job description file

Save the job description as a plain text or markdown file in `job_descriptions/`:

```
job_descriptions/
  senior_cpp_dev.txt
  rust_backend.md
```

### 2. Run the tailor script

```bash
# Preview changes without writing files
python tailor.py job_descriptions/senior_cpp_dev.txt --dry-run

# Generate tailored .tex file
python tailor.py job_descriptions/senior_cpp_dev.txt

# Generate tailored .tex and immediately build PDF
python tailor.py job_descriptions/senior_cpp_dev.txt --build
```

The script adapts only the **Summary** and **Technical Skills** sections to match the job description. The original `yury_bely_cv.tex` is never modified. All skills are reordered by relevance — no new skills are invented.

### Command Reference

```
python tailor.py <job_description> [options]
```

| Flag | Description |
|------|-------------|
| `<job_description>` | (required) Path to job description file |
| `-t`, `--template` | Path to LaTeX template (default: `yury_bely_cv.tex`) |
| `-o`, `--output` | Output .tex path (default: `output/yury_bely_cv_tailored_<date>.tex`) |
| `-b`, `--build` | Build PDF via `build.sh` after generating .tex |
| `--dry-run` | Print tailored Summary and Skills to stdout without writing files |
| `-m`, `--model` | LLM model to use (default: `glm-4.7-flash`) |
| `-v`, `--verbose` | Enable verbose logging |

### Examples

```bash
# Quick preview of what will change
python tailor.py job_descriptions/senior_cpp_dev.txt --dry-run

# Full pipeline: tailor + build PDF
python tailor.py job_descriptions/senior_cpp_dev.txt --build

# Use a specific output name
python tailor.py job_descriptions/senior_cpp_dev.txt -o output/company_x.tex --build

# Use a different model
python tailor.py job_descriptions/senior_cpp_dev.txt -m glm-4.7 --build
```
