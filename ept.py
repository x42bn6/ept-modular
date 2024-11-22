from abc import ABC, abstractmethod

from ortools.sat.python.cp_model import IntVar

from metadata import Metadata
from stage import GroupStage, Stage


class EptStage:
    def __init__(self,
                 stage: Stage,
                 points: [int]):
        if len(points) > stage.team_count:
            raise ValueError(f"Cannot assign more points {points} than team count {stage.team_count}")

        self.stage = stage
        self.points = [points[p] if p < len(points) else 0 for p in range(stage.team_count)]

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
