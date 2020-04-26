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

    def surplus_for_candidate(self, surplus, candidate_name):
        surplus_per_vote = surplus / len(self.__ballots)
        votes_for_candidate = sum(
            [1 for b in self.__ballots if len(b) > 0 and b[0] == candidate_name])
        result = math.floor(votes_for_candidate * surplus_per_vote)
        self.__votes -= result
        return result

    def exhausted_ballots(self, surplus):
        surplus_per_vote = surplus / len(self.__ballots)
        exhausted_votes = sum([1 for b in self.__ballots if len(b) == 0])
        result = math.floor(exhausted_votes * surplus_per_vote)
        self.__votes -= result
        return result

    def add_surplus(self, surplus):
        self.__votes += math.floor(surplus)

    def surplus(self, quota):
        return max(self.__votes - quota, 0.0)

    def add_ballot(self, new_ballot):
        self.__ballots.append(new_ballot)
        self.__votes += 10_000  # add a vote for the corresponding ballot

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
    winner = biggest_winners[-1]
    surplus = winner.surplus(quota)
    for c in candidates:
        c.add_surplus(winner.surplus_for_candidate(surplus, c.name))
    exhausted.add_surplus(winner.exhausted_ballots(surplus))
    return candidates


def redisitribute_loser(candidates, exhausted, round_results):
    """ 
        Returns: A list of Candidates with the lowest vote
            getting Canidate removed
    """
    biggest_losers = [
        c for c in candidates if c.votes == min(candidates).votes]
    eliminated = pick_loser(biggest_losers, round_results)
    candidates.remove(eliminated)

    for b in eliminated.ballots:
        next_choice = b[0] if len(b) > 0 else None
        if(next_choice == None):
            exhausted.add_ballot(b)
        for c in candidates:
            c.drop_candidate(eliminated)
            if c.name == next_choice:
                c.add_ballot(b[1:])

    return candidates


def pick_loser(tied, round_results):
    """ Breaks the tie by recursively picking the candidate with the most 
        votes in the last round.

    Args:
        tied: List[Candidate]
        round_results: List of Tuples of candidate name to votes where each
                       list item is the reults from that round.

    Returns: The candidate that will be redistributed.
    """
    if len(tied) == 1:
        return tied[0]  # There is no tie return sole loser
    if not round_results:
        return tied[0]  # We can't break any remaing ties just pick a loser
    tied_names = [c.name for c in tied]
    rnd = round_results[-1]
    min_votes = min([c for c in rnd if c[0] in tied_names],
                    key=lambda r: r[1])[1]
    loser_names = [c[0]
                   for c in rnd if c[0] in tied_names and c[1] == min_votes]
    loser_candidates = [c for c in tied if c.name in loser_names]

    if(len(loser_candidates) == 1):
        return loser_candidates[0]

    return pick_loser(loser_candidates, round_results[:-1])


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
        winners = {}
        round_results = []
        exhausted = Candidate("Exhausted", [])

        while True:
            num_votes = sum([c.votes for c in candidates_to_votes])
            quota = calculate_quota(num_winners, num_votes)
            candidates_to_votes.sort(reverse=True)
            # Print stats
            print(f"Round {len(round_results) + 1}:")
            print(f"Quota to win: {quota}")
            for c in candidates_to_votes:
                print(f"  {c.name}: {c.votes}")

            round_results.append([(c.name, c.votes)
                                  for c in candidates_to_votes])

            # Update winners
            winners.clear()
            for w in find_winners(candidates_to_votes, quota):
                winners[w.name] = w

            if(len(winners) == num_winners):
                return winners, exhausted
            elif(sum([w.surplus(quota) for w in winners.values()]) > 0.0):
                candidates_to_votes = distribute_surplus(
                    candidates_to_votes, exhausted, quota)
            else:
                candidates_to_votes = redisitribute_loser(
                    candidates_to_votes, exhausted, round_results)
            


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Administer election.')
    parser.add_argument('-f', '--file', action='store', type=str,
                        help='Name of the election results file')
    parser.add_argument('-n', '--num_winners', action='store',
                        type=int, default=1, help='Number of winners to pick')

    args = parser.parse_args()
    winners, exhausted = count_ballots(args.file, num_winners=args.num_winners)
    print("")
    for w in winners.values():
        print(f"🏆: {w}")
    print(f"exhausted votes {exhausted.votes}")
