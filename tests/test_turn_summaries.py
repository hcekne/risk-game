import json
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

from tests.helpers import make_scripted_game_master


pytestmark = pytest.mark.regression


class TurnSummaryTests(unittest.TestCase):
    def test_play_game_saves_turn_summaries_and_analysis_report(self):
        random.seed(13)
        game = make_scripted_game_master(
            "Alpha",
            "Bravo",
            "Charlie",
            territory_control_percentage=0.65,
            max_rounds=4,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            game.play_game(include_initial_troop_placement=True, base_folder=temp_dir)

            game_folders = sorted(Path(temp_dir).glob("game__*"))
            self.assertEqual(len(game_folders), 1)
            game_folder = game_folders[0]

            state_files = sorted(game_folder.glob("game_state_turn_*.csv"))
            summary_files = sorted(game_folder.glob("turn_summary_turn_*.json"))
            self.assertGreater(len(summary_files), 0)
            self.assertEqual(len(summary_files), len(state_files) - 1)

            first_summary = json.loads(summary_files[0].read_text())
            self.assertIn("player", first_summary)
            self.assertIn("plan", first_summary)
            self.assertIn("events", first_summary)
            self.assertIn("derived", first_summary)
            self.assertIn("post_turn", first_summary)
            self.assertTrue(first_summary["plan"]["text"])
            self.assertGreater(len(first_summary["events"]), 0)
            self.assertIn("turn_time_seconds", first_summary["derived"])

            analysis_dir = game_folder / "analysis"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/analyze_turn_summaries.py",
                    "--game-folder",
                    str(game_folder),
                    "--output-dir",
                    str(analysis_dir),
                ],
                cwd=str(Path(__file__).resolve().parents[1]),
                capture_output=True,
                text=True,
                check=True,
            )

            output = json.loads(result.stdout)
            self.assertEqual(output["turn_count"], len(summary_files))
            self.assertTrue((analysis_dir / "strategic_analysis.md").exists())
            self.assertTrue((analysis_dir / "strategic_metrics.json").exists())
            self.assertTrue((analysis_dir / "strategic_turn_scores.json").exists())

            report_text = (analysis_dir / "strategic_analysis.md").read_text()
            self.assertIn("## Turn By Turn", report_text)
            self.assertIn("Plan:", report_text)
            self.assertIn("Rubric: overall=", report_text)

            metrics = json.loads((analysis_dir / "strategic_metrics.json").read_text())
            first_player_metrics = next(iter(metrics.values()))
            self.assertIn("avg_rubric_score", first_player_metrics)
            self.assertIn("avg_rubric_dimensions", first_player_metrics)


if __name__ == "__main__":
    unittest.main()
