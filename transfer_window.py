from abc import ABC

from ortools.sat.python.cp_model import CpSolver

from display_phases import DisplayPhase, HasDisplayPhase, DisplayPhaseType
from teams import TeamDatabase


class TransferWindow(HasDisplayPhase, ABC):
    def __init__(self, name: str, team_database: TeamDatabase):
        super().__init__()
        self.name = name
        self.team_database = team_database
        self.changes = {}

    def add_change(self, team_name: str, delta: int):
        self.changes[self.team_database.get_team_index_by_team_name(team_name)] = delta

    def get_changes(self):
        return self.changes

    def to_display_phases(self, solver: CpSolver) -> [DisplayPhase]:
        display_phase: DisplayPhase = DisplayPhase(self.name, len(self.team_database.get_all_teams()), DisplayPhaseType.TRANSFER_WINDOW)
        for team, delta in self.changes.items():
            display_phase.add_placement(team, None, delta)
        return [display_phase]
