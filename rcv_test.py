import rcv
import unittest
from test import support

class ElectionTest(unittest.TestCase):

    def test_quota(self):
        self.assertTrue(rcv.calculate_quota(num_winners=1, num_votes=10) == 5)
        self.assertTrue(rcv.calculate_quota(num_winners=1, num_votes=100) == 50)
        self.assertTrue(rcv.calculate_quota(num_winners=3, num_votes=100) == 25)

    def test_abc_1(self):
        winners, exhausted = rcv.count_ballots("results/abc.csv", num_winners=1)
        self.assertTrue(len(winners.values()) == 1)
        self.assertTrue(winners["Alice"].name == "Alice")
        self.assertTrue(winners["Alice"].votes == 60_000)
        self.assertTrue(exhausted.votes == 0)

    def test_abc_2(self):
        winners, exhausted = rcv.count_ballots("results/abc.csv", num_winners=2)
        self.assertTrue(len(winners.values()) == 2)
        self.assertTrue(winners["Alice"].name == "Alice")
        self.assertTrue(winners["Bill"].name == "Bill")
        self.assertTrue(winners["Alice"].votes == 30_000)
        self.assertTrue(winners["Bill"].votes == 20_000)
        self.assertTrue(exhausted.votes == 30_000)

    def test_bookclub(self):
        winners, exhausted = rcv.count_ballots("results/book_club_responses.csv", num_winners=1)
        self.assertTrue(len(winners.values()) == 1)
        self.assertTrue(max(winners.values()).name == "[One Day]")
        self.assertTrue(exhausted.votes == 0)

if __name__ == '__main__':
    unittest.main()