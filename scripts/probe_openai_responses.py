import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import OpenAI


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Probe OpenAI Responses API latency and output across model settings."
        )
    )
    parser.add_argument("--model", required=True, help="OpenAI model ID to probe.")
    parser.add_argument(
        "--prompt",
        default=None,
        help="Inline prompt text. Use either --prompt or --prompt-file.",
    )
    parser.add_argument(
        "--prompt-file",
        default=None,
        help="Path to a file containing the prompt text.",
    )
    parser.add_argument(
        "--efforts",
        nargs="+",
        default=["medium", "high"],
        help="Reasoning effort values to test.",
    )
    parser.add_argument(
        "--verbosities",
        nargs="+",
        default=["medium"],
        help="Text verbosity values to test.",
    )
    parser.add_argument(
        "--summaries",
        nargs="+",
        default=["omit", "auto"],
        help=(
            "Reasoning summary values to test. Use 'omit' to not send reasoning.summary."
        ),
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=120.0,
        help="Per-request client timeout.",
    )
    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=128,
        help="Cap output token count for the probe request.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional JSON output path. Defaults under game_results/model_probes/.",
    )
    return parser.parse_args()


def load_prompt(args: argparse.Namespace) -> str:
    if args.prompt:
        return args.prompt
    if args.prompt_file:
        return Path(args.prompt_file).read_text()
    raise ValueError("Provide either --prompt or --prompt-file.")


def extract_reasoning_summaries(response: Any) -> List[str]:
    summaries: List[str] = []
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) != "reasoning":
            continue
        for summary in getattr(item, "summary", []) or []:
            text = getattr(summary, "text", None)
            if text:
                summaries.append(text)
    return summaries


def probe_once(
    *,
    client: OpenAI,
    model: str,
    prompt: str,
    effort: str,
    verbosity: str,
    summary: str,
    timeout_seconds: float,
    max_output_tokens: int,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "model": model,
        "input": prompt,
        "max_output_tokens": max_output_tokens,
        "text": {"verbosity": verbosity},
    }

    reasoning: Dict[str, Any] = {"effort": effort}
    if summary != "omit":
        reasoning["summary"] = summary
    params["reasoning"] = reasoning

    started = time.time()
    try:
        response = client.with_options(timeout=timeout_seconds).responses.create(**params)
        usage = response.usage.model_dump() if getattr(response, "usage", None) else None
        return {
            "model": model,
            "effort": effort,
            "verbosity": verbosity,
            "summary": summary,
            "wall_clock_seconds": round(time.time() - started, 3),
            "status": "ok",
            "response_id": getattr(response, "id", None),
            "output_text": response.output_text,
            "usage": usage,
            "reasoning_summaries": extract_reasoning_summaries(response),
        }
    except Exception as exc:
        return {
            "model": model,
            "effort": effort,
            "verbosity": verbosity,
            "summary": summary,
            "wall_clock_seconds": round(time.time() - started, 3),
            "status": "error",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def main() -> None:
    args = parse_args()
    prompt = load_prompt(args)
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    results = []
    for effort in args.efforts:
        for verbosity in args.verbosities:
            for summary in args.summaries:
                result = probe_once(
                    client=client,
                    model=args.model,
                    prompt=prompt,
                    effort=effort,
                    verbosity=verbosity,
                    summary=summary,
                    timeout_seconds=args.timeout_seconds,
                    max_output_tokens=args.max_output_tokens,
                )
                results.append(result)
                print(
                    f"{args.model} effort={effort} verbosity={verbosity} "
                    f"summary={summary} status={result['status']} "
                    f"time={result['wall_clock_seconds']:.3f}s"
                )
                if result["status"] == "ok":
                    print(f"  text: {result['output_text'][:240]!r}")
                else:
                    print(f"  error: {result['error_type']}: {result['error']}")

    output_path = args.output
    if output_path is None:
        probe_dir = Path("game_results") / "model_probes"
        probe_dir.mkdir(parents=True, exist_ok=True)
        output_path = probe_dir / f"openai_probe_{args.model}_{int(time.time())}.json"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model,
        "prompt": prompt,
        "efforts": args.efforts,
        "verbosities": args.verbosities,
        "summaries": args.summaries,
        "timeout_seconds": args.timeout_seconds,
        "max_output_tokens": args.max_output_tokens,
        "results": results,
    }
    output_path.write_text(json.dumps(payload, indent=2))
    print(f"Saved probe results to {output_path}")


if __name__ == "__main__":
    main()
