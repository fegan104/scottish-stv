from rcv import * 
import unittest
from test import support
import csv

class ElectionTest(unittest.TestCase):

    def test_quota(self):
        self.assertTrue(calculate_quota(num_winners=1, num_votes=10) == 5)
        self.assertTrue(calculate_quota(num_winners=1, num_votes=100) == 50)
        self.assertTrue(calculate_quota(num_winners=3, num_votes=100) == 25)

    def test_abc_1(self):
        winners, exhausted = count_ballots("results/abc.csv", num_winners=1)
        self.assertTrue(len(winners.values()) == 1)
        self.assertTrue(winners["Alice"].name == "Alice")
        self.assertTrue(winners["Alice"].votes == 60_000)
        self.assertTrue(exhausted.votes == 0)

    def test_abc_2(self):
        winners, exhausted = count_ballots("results/abc.csv", num_winners=2)
        self.assertTrue(len(winners.values()) == 2)
        self.assertTrue(winners["Alice"].name == "Alice")
        self.assertTrue(winners["Bill"].name == "Bill")
        self.assertTrue(winners["Alice"].votes == 30_000)
        self.assertTrue(winners["Bill"].votes == 20_000)
        self.assertTrue(exhausted.votes == 30_000)

    def test_bookclub(self):
        winners, exhausted = count_ballots("results/book_club_responses.csv", num_winners=1)
        self.assertTrue(len(winners.values()) == 1)
        self.assertTrue(max(winners.values()).name == "[One Day]")
        self.assertTrue(exhausted.votes == 0)

    def test_elections(self):
        winners, exhausted = count_ballots("results/elections.csv", num_winners=1)
        self.assertTrue(len(winners.values()) == 1)
        self.assertTrue(max(winners.values()).votes == 80_000)
        self.assertTrue(exhausted.votes == 0)

    def test_pick_loser(self):
        with open("results/tie.csv") as csv_file:
            num_winners = 1
            csv_data = csv.reader(csv_file, delimiter=',')
            candidate_names, vote_data = parse_vote_data(csv_data)
            candidates = award_first_pref(candidate_names, vote_data)
            round_results = [[(c.name, c.votes) for c in candidates]]
            num_votes = sum([c.votes for c in candidates])
            exhausted = Candidate("Exhausted", [])
            quota = calculate_quota(num_winners, num_votes)
            tied = [Candidate("Alice", ["Alice"]), Candidate("Bill", ["Alice", "Alice", "Alice", "Alice"])]
            result = pick_loser(tied, round_results)
            self.assertTrue(type(result) is Candidate)
            self.assertTrue(result.name == "Bill")
            self.assertTrue(result.votes == 40_000)

    def test_tie(self):
        winners, exhausted = count_ballots("results/tie.csv", num_winners=1)
        self.assertEqual(1, len(winners))
        self.assertEqual(60_000, max(winners.values()).votes)
        self.assertEqual(60_000, exhausted.votes)

if __name__ == '__main__':
    unittest.main()