"""Tests for letter_check.py. Run: python3 -m unittest test_letter_check (from tools/)."""
import tempfile
import unittest
from pathlib import Path

import letter_check

STRONG = r"""\documentclass{wisletter}
\candidate{Dana}{Levi}
\begin{document}
\opening{Dear Members of the Committee,}

I supervised \fname{} for two years on her MSc thesis, and she is the strongest of the 30 MSc students I have advised since 2015.

She proposed the evaluation protocol herself after our baseline failed; it is now used by two other groups. The resulting paper was accepted at NeurIPS 2025, where she is first author.

She is original and analytical, and she runs her own line of research.

\closing{Sincerely,}
\end{document}
"""

WEAK = r"""\documentclass{wisletter}
\begin{document}
\opening{Dear Committee,}

I have known him since 2024, when he took my course. He may become a good researcher with time.

He is hardworking, diligent and dedicated. He wrote two papers. He lacks experience in writing.

This paragraph describes the most important piece of work the candidate did.

\closing{Sincerely,}
\end{document}
"""


def run(text, **kw):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "main.tex"
        p.write_text(text, encoding="utf-8")
        return letter_check.check(p, **kw)


def entries(rep, level=None):
    return [f["entry"] for f in rep["findings"] if level is None or f["level"] == level]


class TestStrong(unittest.TestCase):
    def setUp(self):
        self.rep = run(STRONG)

    def test_no_residue_or_hedges(self):
        self.assertNotIn("Template residue and names", entries(self.rep))
        self.assertNotIn("No hedges; at most one real limitation", entries(self.rep))

    def test_rank_has_pool_and_window(self):
        self.assertEqual(entries(self.rep, 1), [])

    def test_paper_with_venue_passes(self):
        self.assertNotIn("Describe the research, and translate its currency", entries(self.rep))

    def test_comments_and_preamble_ignored(self):
        self.assertNotIn("documentclass", self.rep["first_paragraph"])


class TestWeak(unittest.TestCase):
    def setUp(self):
        self.rep = run(WEAK, cap_words=20)

    def test_residue(self):
        self.assertIn("Template residue and names", entries(self.rep, letter_check.MECH))

    def test_cap(self):
        self.assertIn("Obey the call before anything else", entries(self.rep, 0))

    def test_hedge_in_first_paragraph(self):
        self.assertIn("The first paragraph carries the verdict", entries(self.rep, 1))

    def test_no_rank(self):
        self.assertIn("A rank is believed only when it is rationed and reproducible",
                      entries(self.rep, 1))

    def test_negative_and_hedge(self):
        whats = [f["what"] for f in self.rep["findings"] if f["level"] == 3]
        self.assertTrue(any("lacks" in w for w in whats))
        self.assertTrue(any("'may'" in w for w in whats))

    def test_paper_without_venue(self):
        self.assertIn("Describe the research, and translate its currency", entries(self.rep, 2))

    def test_effort_over_ability_is_advisory(self):
        whats = [f["what"] for f in self.rep["findings"]]
        self.assertTrue(any(w.startswith("advisory: effort words") for w in whats))


NAMED = r"""\candidate{Noa}{Cohen}
\begin{document}
I have advised \fname{} for a year, and she is the best student I have had in years.

Perhaps Noa will one day lead her own group. Noa is kind of quiet in meetings.

\end{document}
"""


class TestNames(unittest.TestCase):
    def setUp(self):
        self.rep = run(NAMED)

    def test_bare_name_counts_as_candidate(self):
        whats = [f["what"] for f in self.rep["findings"] if f["level"] == 3]
        self.assertTrue(any("'Perhaps'" in w for w in whats))

    def test_literal_name_beside_macro(self):
        whats = [f["what"] for f in self.rep["findings"] if f["level"] == letter_check.MECH]
        self.assertTrue(any("literal name 'Noa'" in w for w in whats))

    def test_bare_years_is_not_a_window(self):
        whats = [f["what"] for f in self.rep["findings"] if f["level"] == 1]
        self.assertTrue(any("time window" in w for w in whats))

    def test_kind_of_is_not_communal(self):
        self.assertEqual(self.rep["stats"]["communal"], 0)


class TestComments(unittest.TestCase):
    def test_percent_comment_stripped_but_escaped_kept(self):
        rep = run("\\begin{document}\nShe is in the top 5\\% of the 40 students I taught in 10 years. "
                  "% might weak\n\n\\end{document}\n")
        self.assertNotIn("No hedges; at most one real limitation", entries(rep))


if __name__ == "__main__":
    unittest.main()
