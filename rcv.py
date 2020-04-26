import csv
import math
import re
import argparse


def calculate_quota(num_winners, num_votes):
    return math.floor(num_votes * (1.0 / (1 + num_winners)))


class Candidate:
    """ A model for representing vote counts.

    Args:
        name: String key for the candidate.
        ballots: A 2D array where each element is a string list of candidate
            names sorted in preferences order.
    """

    def __init__(self, name, ballots):
        self.__name = name
        self.__votes = 10_000 * len(ballots)
        self.__ballots = ballots

    @property
    def votes(self):
        return self.__votes

    @property
    def name(self):
        return self.__name

    @property
    def ballots(self):
        return self.__ballots

    def surplus_for_candidate(self, starting_votes, surplus, candidate_name):
        surplus_per_vote = surplus / len(self.ballots)
        votes_for_candidate = sum(
            [1 for b in self.__ballots if len(b) > 0 and b[0] == candidate_name])
        result = math.ceil(votes_for_candidate * surplus_per_vote)
        self.__votes -= result
        return result

    def exhausted_ballots(self, surplus):
        surplus_per_vote = surplus / (self.votes) * 10_000
        exhausted_votes = sum([1 for b in self.__ballots if len(b) == 0])
        result = math.ceil(exhausted_votes * surplus_per_vote)
        self.__votes -= result
        return result

    def add_surplus(self, surplus):
        self.__votes += math.floor(surplus)

    def surplus(self, quota):
        return max(self.__votes - quota, 0.0)

    def add_ballot(self, new_ballot, votes_per_ballot):
        self.__ballots.append(new_ballot)
        self.__votes += math.floor(votes_per_ballot)

    def drop_candidate(self, candidate):
        for b in self.__ballots:
            if(candidate.name in b):
                b.remove(candidate.name)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{{name: {self.name}, votes: {self.__votes}}}"

    def __lt__(self, other):
        return self.votes < other.votes

    def __eq__(self, other):
        return other is Candidate and self.name == other.name


def award_first_pref(candidate_names, ballot_data):
    """ Generates a list of candidates with their approriate 1st round votes 
        and ballot data.

    Returns:
        list of Candidates.
    """
    num_choices = len(ballot_data)
    FIRST = "1"
    choices = [str(n) for n in range(2, num_choices)]
    ballots = {c: [] for c in candidate_names}
    for row in ballot_data:
        key = candidate_names[row.index(FIRST)]
        value = ballots[key]
        ballots[key] = [
            *value, [candidate_names[row.index(choice)] for choice in choices if choice in row]]

    return [Candidate(name=k, ballots=v) for (k, v) in ballots.items()]


def find_winners(candidates, quota):
    """Returns candidates that have met the quota."""
    return [c for c in candidates if c.votes >= quota]


def distribute_surplus(candidates, exhausted, quota):
    """
        Returns the given list of Candidates with the surplus votes from the 
            Candidate with the most surpluss votes transfered to their next 
            preference.
    """
    max_surplus = max([c.surplus(quota) for c in candidates])
    biggest_winners = [c for c in candidates if c.surplus(quota) == max_surplus]
    winner = biggest_winners[0]
    candidates.remove(winner)
    surplus = winner.surplus(quota)
    starting_votes = winner.votes
    for c in candidates:
        c.drop_candidate(winner)
        c.add_surplus(winner.surplus_for_candidate(starting_votes, surplus, c.name))
    exhausted.add_surplus(winner.exhausted_ballots(surplus))
    return candidates


def redisitribute_loser(candidates, exhausted):
    """ 
        Returns: A list of Candidates with the lowest vote
            getting Canidate removed
    """
    fewest_votes = min(candidates).votes
    biggest_losers = [c for c in candidates if c.votes == fewest_votes]
    eliminated = biggest_losers[-1]
    candidates.remove(eliminated)

    starting_votes = eliminated.votes
    for b in eliminated.ballots:
        next_choice = b[0] if len(b) > 0 else None
        if(next_choice == None):
            exhausted.add_ballot(b, eliminated.votes)
        for c in candidates:
            c.drop_candidate(eliminated)
            if c.name == next_choice:
                c.add_ballot(b[1:], starting_votes / len(eliminated.ballots))

    return candidates


def parse_vote_data(csv_data):
    """ Retrieves candidate names from the input file, cleans ballots rows
        such that contain only the numeric ranked preference number. This
        function also discards invalid ballots.

    Returns: A String[] of names, and a String[][] where each row is a String[]
        representating a ballot. Each row item is a stringified integer 
        representing the index of the corresponding candidate in the candidates
        array, or an empty string if the ballot does not rank all candidates.
    """

    def valid(ballot, num_candidates):
        prefs = [int(p) for p in ballot if p]
        if(len(prefs) == 0 or len(prefs) > num_candidates):
            return False

        return sorted(prefs) == list(range(1, len(prefs) + 1))

    candidate_names = [n.strip() for n in next(csv_data)]

    parsed_vote_data = []
    for row in csv_data:
        ballot = [re.sub(r"\D", "", c) for c in row]
        if(valid(ballot, len(candidate_names))):
            parsed_vote_data.append(ballot)
        else:
            print(f"❌ {ballot}")

    return candidate_names, parsed_vote_data


def count_ballots(file_name, num_winners):
    with open(file_name) as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        candidate_names, vote_data = parse_vote_data(csv_data)
        candidates_to_votes = award_first_pref(candidate_names, vote_data)
        round_num = 1
        exhausted = Candidate("Exhausted", [])
        winners = []

        while True:
            num_votes = sum([c.votes for c in candidates_to_votes])
            quota = calculate_quota(num_winners, num_votes)
            candidates_to_votes.sort(reverse=True)
            # Print stats
            print(f"Round {round_num}:")
            for w in winners:
                print(f"🏆: {w}")
            print(f"Votes: {num_votes + exhausted.votes + sum([w.votes for w in winners])}")
            print(f"Quota to win: {quota}")
            for c in candidates_to_votes:
                print(f"  {c.name}: {c.votes}")
            print(f"  Exhausted: {exhausted.votes}")

            # Update winners
            round_winners = find_winners(candidates_to_votes, quota)
            for w in round_winners:
                winners.append(w)

            if(len(winners) >= num_winners):
                return winners[:num_winners], exhausted
            elif(sum([w.surplus(quota) for w in round_winners]) > 0.0):
                candidates_to_votes = distribute_surplus(
                    candidates_to_votes, exhausted, quota)
            else:
                candidates_to_votes = redisitribute_loser(
                    candidates_to_votes, exhausted)
            
            round_num += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Administer election.')
    parser.add_argument('-f', '--file', action='store', type=str,
                        help='Name of the election results file')
    parser.add_argument('-n', '--num_winners', action='store',
                        type=int, default=1, help='Number of winners to pick')

    args = parser.parse_args()
    winners, exhausted = count_ballots(args.file, num_winners=args.num_winners)
    print("")
    for w in winners:
        print(f"🏆: {w}")
    print(f"exhausted votes {exhausted.votes}")
