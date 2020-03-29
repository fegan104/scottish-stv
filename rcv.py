import csv
import math


def quota(num_winners, num_votes):
    return math.floor(num_votes * (1.0 / (1 + num_winners)))


class Candidate:
    """ A model for representing vote counts.

    Args:
        name: String key for the candidate.
        ballots: A 2D array where each element is a list candidate
            names sorted in preferences order.
    """

    def __init__(self, name, ballots):
        self.name = name
        self.__votes = len(ballots)
        self.__ballots = ballots

    def votes(self):
        return self.__votes

    def add_surplus(self, surplus):
        self.__votes += surplus

    def surplus(self, threshold):
        return max(self.__votes - threshold, 0)

    def add_ballots(self, new_ballots):
        self.__ballots.append(new_ballots)
        self.__votes = len(self.__ballots)

    def drop_candidate(self, candidate):
        self.__ballots.remove(candidate)

    def __str__(self):
        return f"{{name: {self.name}, votes: {self.__votes}}}"


def award_first_pref(candidates, ballot_data):
    FIRST = "1st Choice"
    choices = [  # TODO generate these dynamicly
        "2nd Choice",
        "3rd Choice",
        "4th Choice",
        "5th Choice",
    ]
    ballots = {c: Candidate(name=c, ballots=[]) for c in candidates}
    stripped_ballot_data = [row[1:] for row in ballot_data]
    for row in stripped_ballot_data:
        key = candidates[row.index(FIRST)]
        value = ballots[key]
        value.add_ballots(
            [candidates[row.index(choice)] for choice in choices if choice in row])

    for (k, v) in ballots.items():
        print(f"{v}")

    return ballots, len(stripped_ballot_data)


def find_winners(candidates_to_votes, quota):
    return " [Vanilla]"


def distribute_surplus(candidates_to_votes):
    return candidates_to_votes


def redisitribute_loser(candidates_to_votes):
    return candidates_to_votes


def count_ballots(file_name, num_winners):
    with open(file_name) as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        candidates = next(csv_data)[1:]
        candidates_to_votes, num_votes = award_first_pref(candidates, csv_data)
        winners = []
        while len(winners) < num_winners:
            wins = find_winners(candidates_to_votes,
                                quota(num_winners, num_votes))
            winners.append(wins)
            if(len(winners) >= num_winners):
                return winners
            elif(len(wins) > 0):
                candidates_to_votes = distribute_surplus(candidates_to_votes)
            else:
                candidates_to_votes = redisitribute_loser(candidates_to_votes)
        return winners


if __name__ == "__main__":
    print(f"WINNER: {count_ballots('ice_cream_responses.csv', num_winners=1)}")
