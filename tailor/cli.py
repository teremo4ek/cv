"""CLI for resume tailoring script."""

import argparse
import logging
import sys

from .tailorer import tailor_resume, DEFAULT_MODEL


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tailor resume Summary and Skills for a specific job description."
    )
    parser.add_argument(
        "job_description",
        help="Path to job description file (text or markdown)",
    )
    parser.add_argument(
        "-t", "--template",
        default="yury_bely_cv.tex",
        help="Path to LaTeX template (default: yury_bely_cv.tex)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output .tex path (default: output/yury_bely_cv_tailored_<date>.tex)",
    )
    parser.add_argument(
        "-b", "--build",
        action="store_true",
        help="Build PDF via build.sh after generating .tex",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print tailored sections to stdout without writing files",
    )
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        help="LLM model to use (default: glm-4.7-flash)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        tailor_resume(
            job_description_path=args.job_description,
            template_path=args.template,
            output_path=args.output,
            model=args.model,
            build=args.build,
            dry_run=args.dry_run,
        )
    except SystemExit as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        sys.exit(2)
