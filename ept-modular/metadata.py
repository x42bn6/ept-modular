
from ortools.sat.python.cp_model import CpModel, IntVar
from teams import TeamDatabase


class Metadata:
    def __init__(self,
                 team_database: TeamDatabase,
                 model: CpModel):
        self.team_database = team_database
        self.model = model
