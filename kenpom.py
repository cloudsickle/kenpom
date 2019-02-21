"""
Extract team data from kenpom.com.

The kenpom module parses the html of kenpom.com, and builds Team objects
to store team information and statistics.

Usage is quite simple.

>>> import kenpom
>>> kp = kenpom.get()
>>> uk = kp['Kentucky']
>>> if uk.rank != 1:
        print('Not that good this year!')

The returned object from get() is a dictionary where the keys are team
names and the values are instances of the kenpom.Team class.

For more information on the meaning of particular team statistics, and
how they are calculated, refer to kenpom.com.
"""
from dataclasses import dataclass

from urllib.request import urlopen
from html.parser import HTMLParser


@dataclass
class Team:
    """
    Store team information and statistics.

    Most attributes have long and short names, for example:
        team.defense == team.d

    Available attributes:
        rank
        name
        conference
        wins, w
        losses, l
        efficiency, e
        offense, o
        defense, d
        tempo, t
        luck
        opponent_efficiency, o_e
        opponent_offense, o_o
        opponent_defense, o_d
        nonconference_opponent_efficiency, nc_o_e
        record

    For more information on what these values mean, refer to kenpom.com.
    """
    rank: int
    name: str
    conference: str
    wins: int
    losses: int
    efficiency: float
    offense: float
    defense: float
    tempo: float
    luck: float
    opponent_efficiency: float
    opponent_offense: float
    opponent_defense: float
    nonconference_opponent_efficiency: float

    @property
    def d(self):
        return self.defense

    @property
    def e(self):
        return self.efficiency

    @property
    def l(self):
        return self.losses

    @property
    def nc_o_e(self):
        return self.nonconference_opponent_efficiency

    @property
    def o(self):
        return self.offense

    @property
    def o_d(self):
        return self.opponent_defense

    @property
    def o_e(self):
        return self.opponent_efficiency

    @property
    def o_o(self):
        return self.opponent_offense

    @property
    def record(self):
        return '-'.join((self.wins, self.losses))

    @property
    def t(self):
        return self.tempo

    @property
    def w(self):
        return self.wins


class KenPomParser(HTMLParser):
    """Parse the HTML of kenpom.com, extracting team data."""
    def __init__(self):
        super(KenPomParser, self).__init__()

        self.row = None
        self.rows = []
    
    def handle_starttag(self, tag, attrs):
        """Look for the start of a table row."""
        if tag == 'tr':
            self.row = []

    def handle_endtag(self, tag):
        """Look for the end of a table row."""
        if tag == 'tr':
            if len(self.row) == 22:
                self.rows.append(self.row[1:])
            self.row = None

    def handle_data(self, data):
        """Include team data from the table."""
        if type(self.row) == list:
            self.row.append(data)


def get():
    """Parse kenpom.com and return a team data lookup (dictionary)."""
    with urlopen('https://www.kenpom.com') as kp:
        kp_html = kp.read().decode('utf-8')

    parser = KenPomParser()
    parser.feed(kp_html)    

    return _create_teams(parser.rows)


def _create_teams(team_data):
    """Build a team lookup from kenpom table data."""
    teams = {}

    for (rank, name, conf, rec, e, o, _, d, _, t, _, luck, _,
             o_e, _, o_o, _, o_d, _, nc_o_e, _) in team_data:

            wins, losses = rec.split('-')

            rank, wins, losses = map(int, (rank, wins, losses))
            e, o, d, t, luck = map(float, (e, o, d, t, luck))
            o_e, o_o, o_d, nc_o_e = map(float, (o_e, o_o, o_d, nc_o_e))

            teams[name] = Team(rank, name, conf, wins, losses,
                               e, o, d, t, luck, o_e, o_o, o_d, nc_o_e)

    return teams


if __name__ == '__main__':
    pass
