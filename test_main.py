import contextlib
import io
import unittest
from unittest.mock import patch

from main import main


class SimulateTests(unittest.TestCase):
    def test_simulate_prints_battle_statistics(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["--simulate", "4", "--x", "winning", "--o", "random", "--seed", "1"])
        text = out.getvalue()
        self.assertIn("Played 4 games", text)
        self.assertIn("winning (X) vs random (O)", text)
        self.assertIn("X wins", text)
        self.assertIn("Draws", text)

    def test_simulate_rejects_human_players(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                main(["--simulate", "2", "--x", "human"])

    def test_simulate_defaults_to_two_random_ais(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["--simulate", "3", "--seed", "1"])
        self.assertIn("random (X) vs random (O)", out.getvalue())


class InteractiveTests(unittest.TestCase):
    @patch("builtins.input", side_effect=EOFError)
    def test_exits_gracefully_when_input_closes_mid_game(self, _):
        with contextlib.redirect_stdout(io.StringIO()):
            main([])


if __name__ == "__main__":
    unittest.main()
