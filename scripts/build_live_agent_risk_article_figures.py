import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path("/app")
REPO_ROOT = Path("/app")
SHARED_ROOT = Path("/shared-game-results")

OUT_DIR = REPO_ROOT / "docs" / "article-plans" / "assets" / "2026-05-10_live-agent-risk"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COLOR = {
    "Gemini": "#1f77b4",
    "Claude": "#2ca02c",
    "OpenAI": "#d62728",
    "Kimi": "#9467bd",
    "Anchor": "#8c564b",
}


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def save_figure(fig: plt.Figure, stem: str):
    png = OUT_DIR / f"{stem}.png"
    pdf = OUT_DIR / f"{stem}.pdf"
    fig.tight_layout()
    fig.savefig(png, dpi=220, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return {"png": str(png), "pdf": str(pdf)}


def provider_fullstack_wins():
    data = load_json(
        SHARED_ROOT / "experiment_series" / "frontier_strategic_provider_32_pooled" / "series_summary.json"
    )
    mapping = {
        "gemini-3.1-pro-preview": "Gemini",
        "gpt-5.1": "OpenAI",
        "claude-opus-4-7": "Claude",
        "kimi-k2.6": "Kimi",
    }
    items = [(mapping[k], v) for k, v in data["win_counts"].items()]
    items.sort(key=lambda x: x[1], reverse=True)
    labels = [k for k, _ in items]
    values = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    bars = ax.bar(labels, values, color=[COLOR[label] for label in labels])
    ax.set_title("Full-Stack Provider Championship (32 Games)")
    ax.set_ylabel("Wins")
    ax.set_ylim(0, max(values) + 4)
    ax.axhline(8, color="#666666", linestyle="--", linewidth=1, alpha=0.6)
    ax.text(3.1, 8.4, "equal-win baseline = 8", color="#666666", fontsize=9)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.25, str(value), ha="center", va="bottom")
    return save_figure(fig, "fig01_provider_fullstack_wins")


def kimi_anchor_comparison():
    paths = [
        (
            "GPT-4.1 anchor",
            SHARED_ROOT / "experiments" / "experiment__2026-05-07_15-34-43__kimi_anchor_openai_gpt41_team_16" / "experiment_summary.json",
            "gpt-4.1",
        ),
        (
            "Gemini 2.5 Pro anchor",
            SHARED_ROOT / "experiments" / "experiment__2026-05-07_15-35-19__kimi_anchor_gemini25pro_team_16" / "experiment_summary.json",
            "gemini-2.5-pro",
        ),
        (
            "Claude Sonnet 4 anchor",
            SHARED_ROOT / "experiments" / "experiment__2026-05-07_17-43-42__kimi_anchor_anthropic_sonnet4_20250514_team_16" / "experiment_summary.json",
            "claude-sonnet-4-20250514",
        ),
    ]
    labels, kimi_wins, anchor_wins = [], [], []
    for label, path, anchor_prefix in paths:
        data = load_json(path)
        labels.append(label)
        kw = sum(v for k, v in data["win_counts"].items() if k.startswith("kimi-k2.6"))
        aw = sum(v for k, v in data["win_counts"].items() if k.startswith(anchor_prefix))
        kimi_wins.append(kw)
        anchor_wins.append(aw)

    x = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(10.2, 5.4))
    b1 = ax.bar(x - width / 2, kimi_wins, width, label="Kimi team", color=COLOR["Kimi"])
    b2 = ax.bar(x + width / 2, anchor_wins, width, label="Anchor team", color=COLOR["Anchor"])
    ax.set_title("Kimi Capability Anchors (16 Games Each)")
    ax.set_ylabel("Wins")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=10, ha="right")
    ax.set_ylim(0, 12)
    ax.legend()
    for bars in (b1, b2):
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15, f"{int(bar.get_height())}", ha="center", va="bottom", fontsize=9)
    return save_figure(fig, "fig02_kimi_anchor_comparison")


def gemini_cost_gate():
    data = load_json(
        SHARED_ROOT / "experiment_series" / "gemini3_flash_execution_cost_gate_15_pooled" / "series_summary.json"
    )
    rename = {
        "gemini-3.1-pro-full": "3.1 Pro full",
        "gemini-3.1-plan_gemini-3-flash-exec": "3.1 plan + 3 Flash exec",
        "gemini-3-flash-full": "3 Flash full",
    }
    order = [
        "gemini-3.1-pro-full",
        "gemini-3.1-plan_gemini-3-flash-exec",
        "gemini-3-flash-full",
    ]
    wins = [data["win_counts"][k] for k in order]
    costs = [data["players"][k]["estimated_total_cost_usd"] for k in order]

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    axes[0].bar(range(3), wins, color=[COLOR["Gemini"]] * 3)
    axes[0].set_xticks(range(3))
    axes[0].set_xticklabels([rename[k] for k in order], rotation=15, ha="right")
    axes[0].set_ylabel("Wins")
    axes[0].set_title("Wins")
    for i, v in enumerate(wins):
        axes[0].text(i, v + 0.1, str(v), ha="center", va="bottom")

    axes[1].bar(range(3), costs, color=["#7aa6d8", "#3f88c5", "#a5c8e1"])
    axes[1].set_xticks(range(3))
    axes[1].set_xticklabels([rename[k] for k in order], rotation=15, ha="right")
    axes[1].set_ylabel("Estimated total cost (USD)")
    axes[1].set_title("Estimated API cost")
    for i, v in enumerate(costs):
        axes[1].text(i, v + 0.03, f"${v:.2f}", ha="center", va="bottom")

    fig.suptitle("Gemini Execution Cost Gate (15 Games)")
    return save_figure(fig, "fig03_gemini_cost_gate")


def planner_compression():
    full = load_json(
        SHARED_ROOT / "experiment_series" / "frontier_strategic_provider_32_pooled" / "series_summary.json"
    )
    plan = load_json(
        SHARED_ROOT / "experiment_series" / "gemini3_flash_execution_planner_hybrid_bakeoff_32_pooled" / "series_summary.json"
    )

    full_mapping = {
        "gemini-3.1-pro-preview": ("Gemini", full["win_counts"]["gemini-3.1-pro-preview"]),
        "claude-opus-4-7": ("Claude", full["win_counts"]["claude-opus-4-7"]),
        "gpt-5.1": ("OpenAI", full["win_counts"]["gpt-5.1"]),
        "kimi-k2.6": ("Kimi", full["win_counts"]["kimi-k2.6"]),
    }
    plan_mapping = {
        "gemini-3.1-plan_gemini-3-flash-exec": ("Gemini", plan["win_counts"]["gemini-3.1-plan_gemini-3-flash-exec"]),
        "claude-opus-4-7-plan_gemini-3-flash-exec": ("Claude", plan["win_counts"]["claude-opus-4-7-plan_gemini-3-flash-exec"]),
        "gpt-5.5-plan_gemini-3-flash-exec": ("OpenAI", plan["win_counts"]["gpt-5.5-plan_gemini-3-flash-exec"]),
        "kimi-k2.6-plan_gemini-3-flash-exec": ("Kimi", plan["win_counts"]["kimi-k2.6-plan_gemini-3-flash-exec"]),
    }
    providers = ["Gemini", "Claude", "OpenAI", "Kimi"]
    full_vals = [next(v for name, v in full_mapping.values() if name == p) for p in providers]
    plan_vals = [next(v for name, v in plan_mapping.values() if name == p) for p in providers]

    x = np.arange(len(providers))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9.8, 5.2))
    b1 = ax.bar(x - width / 2, full_vals, width, label="Full-stack provider field", color="#4c78a8")
    b2 = ax.bar(x + width / 2, plan_vals, width, label="Planner-only with shared Flash execution", color="#72b7b2")
    ax.set_xticks(x)
    ax.set_xticklabels(providers)
    ax.set_ylabel("Wins in pooled 32-game series")
    ax.set_title("Provider Spread Compresses When Execution Is Standardized")
    ax.legend()
    for bars in (b1, b2):
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15, f"{int(bar.get_height())}", ha="center", va="bottom", fontsize=9)
    return save_figure(fig, "fig04_planner_compression")


def goal_directedness():
    data = load_json(
        SHARED_ROOT / "experiment_series" / "frontier_strategic_provider_32_pooled" / "trace_analysis" / "planning_trace_metrics.json"
    )
    order = [
        ("gemini-3.1-pro-preview", "Gemini"),
        ("claude-opus-4-7", "Claude"),
        ("gpt-5.1", "OpenAI"),
        ("kimi-k2.6", "Kimi"),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.8))
    labels = [label for _, label in order]
    explicit = [data["players"][k]["feature_metrics"]["explicit_endgame_goal"]["plan_share"] for k, _ in order]
    quantified = [data["players"][k]["feature_metrics"]["quantified_goal"]["plan_share"] for k, _ in order]
    x = np.arange(len(labels))
    width = 0.35
    axes[0].bar(x - width / 2, explicit, width, label="Explicit endgame goal", color="#4c78a8")
    axes[0].bar(x + width / 2, quantified, width, label="Quantified goal", color="#f58518")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels)
    axes[0].set_ylim(0, 0.75)
    axes[0].set_ylabel("Share of plans")
    axes[0].set_title("Goal-Tracking Language by Provider")
    axes[0].legend()

    bands = ["early_0_9", "mid_10_19", "late_20_plus"]
    band_labels = ["0-9 territories", "10-19", "20+"]
    for key, label in order:
        shares = [data["players"][key]["goal_share_by_start_territory_band"].get(b, 0) for b in bands]
        axes[1].plot(band_labels, shares, marker="o", linewidth=2.2, label=label, color=COLOR[label])
    axes[1].set_ylim(0, 1.05)
    axes[1].set_ylabel("Share of plans with explicit goal language")
    axes[1].set_title("Gemini Goal Tracking Scales With Proximity To Victory")
    axes[1].legend(loc="upper left")
    return save_figure(fig, "fig05_goal_directedness")


def execution_chain_distribution():
    data = load_json(
        SHARED_ROOT / "experiment_series" / "frontier_strategic_provider_32_pooled" / "trace_analysis" / "execution_trace_metrics.json"
    )
    order = [
        ("gemini-3.1-pro-preview", "Gemini"),
        ("claude-opus-4-7", "Claude"),
        ("gpt-5.1", "OpenAI"),
        ("kimi-k2.6", "Kimi"),
    ]
    buckets = ["0", "1", "2_3", "4_5", "6_plus"]
    bucket_labels = ["0", "1", "2-3", "4-5", "6+"]
    bucket_colors = ["#d9d9d9", "#9ecae1", "#6baed6", "#3182bd", "#08519c"]

    fig, ax = plt.subplots(figsize=(10.0, 5.6))
    bottom = np.zeros(len(order))
    x = np.arange(len(order))
    for bucket, bucket_label, color in zip(buckets, bucket_labels, bucket_colors):
        vals = [data["players"][k]["attack_chain_distribution"][bucket] for k, _ in order]
        ax.bar(x, vals, bottom=bottom, label=bucket_label, color=color, edgecolor="white")
        bottom += np.array(vals)
    ax.set_xticks(x)
    ax.set_xticklabels([label for _, label in order])
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Share of turns")
    ax.set_title("Execution Chain Depth Distribution")
    ax.legend(title="Successful conquests in turn", ncol=5, bbox_to_anchor=(0.5, 1.18), loc="upper center")
    return save_figure(fig, "fig06_execution_chain_distribution")


def execution_profile_heatmap():
    data = load_json(
        SHARED_ROOT / "experiment_series" / "frontier_strategic_provider_32_pooled" / "trace_analysis" / "execution_trace_metrics.json"
    )
    order = [
        ("gemini-3.1-pro-preview", "Gemini"),
        ("claude-opus-4-7", "Claude"),
        ("gpt-5.1", "OpenAI"),
        ("kimi-k2.6", "Kimi"),
    ]
    rows = [
        ("midgame_avg_territory_delta", "Midgame territories gained"),
        ("long_chain_ge6_turn_share", "6+ conquest turns"),
        ("turns_with_exec_fallback_share", "Execution fallback turns"),
        ("zero_attack_turn_share", "Zero-attack turns"),
        ("phase_metrics.troop_placement.invalid_rate", "Placement invalid rate"),
    ]
    matrix = []
    for metric_key, _ in rows:
        vals = []
        for key, _label in order:
            player = data["players"][key]
            if metric_key.startswith("phase_metrics."):
                _, phase, field = metric_key.split(".")
                vals.append(player["phase_metrics"].get(phase, {}).get(field, 0) or 0)
            else:
                vals.append(player[metric_key] or 0)
        matrix.append(vals)
    arr = np.array(matrix, dtype=float)
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    im = ax.imshow(arr, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([label for _, label in order])
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([label for _, label in rows])
    ax.set_title("Execution Profile Summary")
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            val = arr[i, j]
            txt = f"{val:.3f}" if val < 1 else f"{val:.2f}"
            ax.text(j, i, txt, ha="center", va="center", color="black", fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return save_figure(fig, "fig07_execution_profile_heatmap")


def main():
    manifest = {
        "fig01_provider_fullstack_wins": provider_fullstack_wins(),
        "fig02_kimi_anchor_comparison": kimi_anchor_comparison(),
        "fig03_gemini_cost_gate": gemini_cost_gate(),
        "fig04_planner_compression": planner_compression(),
        "fig05_goal_directedness": goal_directedness(),
        "fig06_execution_chain_distribution": execution_chain_distribution(),
        "fig07_execution_profile_heatmap": execution_profile_heatmap(),
    }
    manifest_path = OUT_DIR / "figure_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(json.dumps({"output_dir": str(OUT_DIR), "manifest": str(manifest_path)}, indent=2))


if __name__ == "__main__":
    plt.style.use("seaborn-v0_8-whitegrid")
    main()
