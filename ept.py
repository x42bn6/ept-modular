from abc import ABC, abstractmethod
from math import floor

from ortools.sat.python.cp_model import IntVar

from metadata import Metadata
from stage import GroupStage, Stage, Tournament, PairGroupStage


class EptStage:
    def __init__(self,
                 stage: Stage,
                 points: [int]):
        if len(points) > stage.team_count:
            raise ValueError(f"Cannot assign more points {points} than team count {stage.team_count}")

        self.stage = stage
        self.points = [points[p] if p < len(points) else 0 for p in range(stage.team_count)]
        self.build()

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def get_points(self) -> [IntVar]:
        pass


class EptGroupStage(EptStage, ABC):
    def __init__(self,
                 stage: GroupStage,
                 points: [int]):
        super().__init__(stage, points)
        self.obtained_points: [IntVar] = []
        self.build()

    def build(self):
        metadata: Metadata = self.stage.metadata
        team_database = metadata.team_database
        self.obtained_points: [IntVar] = [metadata.model.new_int_var(0, 99999, f'd_{self.stage.name}_{i}')
                                          for i in range(len(team_database.get_all_teams()))]
        for team in team_database.get_all_teams():
            team_index = team_database.get_team_index(team)
            self.obtained_points[team_index] = sum(
                self.stage.indicators[team_index][p] * self.points[p] for p in range(len(self.points)))
        pass

    def get_points(self) -> [IntVar]:
        pass

class EptPairGroupStage(EptStage, ABC):
    def __init__(self,
                 stage: PairGroupStage,
                 points: [int]):
        super().__init__(stage, points)
        self.obtained_points: [IntVar] = []
        self.build()

    def build(self):
        metadata: Metadata = self.stage.metadata
        team_database = metadata.team_database
        self.obtained_points: [IntVar] = [metadata.model.new_int_var(0, 99999, f'd_{self.stage.name}_{i}')
                                          for i in range(len(team_database.get_all_teams()))]

        points_extended = [self.points[floor(p / 2)] if floor(p / 2) < len(self.points) else 0 for p in
                               range(self.stage.team_count)]

        for team in team_database.get_all_teams():
            team_index = team_database.get_team_index(team)
            self.obtained_points[team_index] = sum(
                self.stage.indicators[team_index][p] * points_extended[p] for p in range(len(points_extended)))
        pass

    def get_points(self) -> [IntVar]:
        pass

class EptTournament:
    def __init__(self,
                 tournament: Tournament,
                 points: [int]):
        self.tournament = tournament
        self.points = points
        self.obtained_points: [IntVar] = []
        self.build()

    def build(self):
        metadata: Metadata = self.tournament.metadata
        team_database = metadata.team_database
        self.obtained_points: [IntVar] = [metadata.model.new_int_var(0, 99999, f'd_{self.tournament.name}_{i}')
                                          for i in range(len(team_database.get_all_teams()))]
        for team in team_database.get_all_teams():
            team_index = team_database.get_team_index(team)
            self.obtained_points[team_index] = sum(
                self.tournament.indicators[team_index][p] * self.points[p] for p in range(len(self.points)))
        pass
