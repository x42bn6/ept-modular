from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict

from ortools.sat.python.cp_model import CpSolver

from teams import Team

class DisplayPhaseType(Enum):
    TOURNAMENT = 1,
    TRANSFER_WINDOW = 2

class Placement:
    def __init__(self, team: Team, place: int | None, points: int | None):
        self.team = team
        self.place: int | None = place
        self.points: int | None = points

    def __str__(self):
        return f"{self.team.name} => n={self.place}; points={self.points}"


class DisplayPhase:
    def __init__(self, name: str, team_count: int, display_phase_type: DisplayPhaseType):
        self.name: str = name
        self.team_count = team_count
        self.display_phase_type = display_phase_type
        self.placements: Dict[int, Placement] = {}
        self.team_to_place: Dict[Team, int] = {}

    def add_placement(self, team: Team, place: int | None, points: int | None):
        self.placements[place] = Placement(team, place, points)
        self.team_to_place[team] = place

    def get_placement_for_team(self, team: Team) -> Placement | None:
        # Wasn't in this phase
        if team not in self.team_to_place:
            return None

        return self.placements[self.team_to_place[team]]



class HasDisplayPhase(ABC):
    @abstractmethod
    def to_display_phases(self, solver: CpSolver) -> [DisplayPhase]:
        pass
