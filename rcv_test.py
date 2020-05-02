from rcv import * 
import unittest
from test import support
import csv

class ElectionTest(unittest.TestCase):

    def test_quota(self):
        self.assertEquals(calculate_quota(num_winners=1, num_votes=10), 5)
        self.assertEquals(calculate_quota(num_winners=1, num_votes=100), 50)
        self.assertEquals(calculate_quota(num_winners=3, num_votes=100), 25)

    def test_abc_1(self):
        winners, exhausted = count_ballots("results/abc.csv", num_winners=1)
        self.assertEquals(len(winners), 1)
        self.assertEquals(winners[0].name, "Alice")
        self.assertEquals(winners[0].votes, 60_000)
        self.assertEquals(exhausted.votes, 0)

    def test_abc_2(self):
        winners, exhausted = count_ballots("results/abc.csv", num_winners=2)
        self.assertEquals(len(winners),  2)
        self.assertEquals(winners[0].name,  "Alice")
        self.assertEquals(winners[1].name,  "Bill")
        self.assertEquals(winners[0].votes,  30_000)
        self.assertEquals(winners[1].votes,  20_000)
        self.assertEquals(exhausted.votes,  30_000)

    def test_bookclub(self):
        winners, exhausted = count_ballots("results/book_club_responses.csv", num_winners=1)
        self.assertEquals(len(winners),  1)
        self.assertEquals(max(winners).name,  "[One Day]")
        self.assertEquals(exhausted.votes,  0)

    def test_elections(self):
        winners, exhausted = count_ballots("results/elections.csv", num_winners=1)
        self.assertEquals(len(winners),  1)
        self.assertEquals(max(winners).votes,  40_000)
        self.assertEquals(exhausted.votes,  0)

    def test_tie(self):
        winners, exhausted = count_ballots("results/tie.csv", num_winners=1)
        self.assertEqual(1, len(winners))
        self.assertEqual(60_000, max(winners).votes)

    def test_7_way_3(self):
        winners, exhausted = count_ballots("results/seven_way.csv", num_winners=3)
        self.assertEqual(3, len(winners))
        self.assertAlmostEqual(35_000, winners[0].votes, delta=1.0)
        self.assertIn(winners[1].name, ["Alice", "Fred", "Greg"])
        self.assertIn(winners[2].name, ["Alice", "Fred", "Greg"])
        self.assertNotEqual(winners[2].name, winners[1].name)

    def test_7_way_1(self):
        winners, exhausted = count_ballots("results/seven_way.csv", num_winners=1)
        self.assertEqual(1, len(winners))
        self.assertEqual("Dave", winners[0].name)

if __name__ ==  '__main__':
    unittest.main()