from math import floor

from ortools.constraint_solver.pywrapcp import BooleanVar
from ortools.sat.python.cp_model import CpModel
from abc import ABC, abstractmethod

from select import error

from metadata import Metadata
from teams import Team


class Stage(ABC):
    def __init__(self,
                 name: str,
                 team_count: int,
                 metadata: Metadata):
        self.name = name
        self.team_count: int = team_count
        self.metadata: Metadata = metadata
        self.indicators: [[BooleanVar]] = None

    def build(self):
        all_team_count: int = len(self.metadata.team_database.get_all_teams())
        self.indicators: [[BooleanVar]] = [
            [self.metadata.model.new_bool_var(f'x_{self.name}_{i}_{j}') for j in range(self.team_count)]
            for i in range(all_team_count)]

        # One placement per team
        model: CpModel = self.metadata.model
        for placement in range(self.team_count):
            model.Add(
                sum(self.indicators[i][placement] for i in range(all_team_count)) == 1)

        self.add_team_constraints()

    @abstractmethod
    def add_team_constraints(self):
        pass

    @abstractmethod
    def bind_forward(self,
                     stage: "Stage"):
        pass


# Hard-coded list of teams, intended to be the root.  Consider, say, closed qualifiers
class Root(Stage, ABC):
    def __init__(self,
                 name: str,
                 team_count: int,
                 metadata: Metadata,
                 teams: [Team]):
        super().__init__(name, team_count, metadata)
        self.teams = teams

    def add_team_constraints(self):
        pass

    def bind_forward(self, stage: "Stage"):
        model: CpModel = self.metadata.model

        # Every team here makes it through to the next Stage
        # They will place *somewhere* in the next Stage
        for team in self.teams:
            team_index: int = self.metadata.team_database.get_team_index(team)
            model.Add(sum(stage.indicators[team_index]) == 1)
        pass


class GroupStage(Stage, ABC):
    def __init__(self,
                 name: str,
                 team_count: int,
                 advancing_team_count: int,
                 metadata: Metadata):
        if advancing_team_count > team_count:
            raise ValueError(f"Advancing team count {advancing_team_count} must be less than team count {team_count}")

        super().__init__(name, team_count, metadata)
        self.advancing_team_count = advancing_team_count

    def add_team_constraints(self):
        pass

    def bind_forward(self, stage: "Stage"):
        model: CpModel = self.metadata.model

        # Top N teams make it through to the next Stage
        # They will place *somewhere* in the next Stage
        for team in self.metadata.team_database.get_all_teams():
            top_n: [BooleanVar] = model.new_bool_var(f"{self.name}_{team.name}_top_{self.advancing_team_count}")
            team_index: int = self.metadata.team_database.get_team_index(team)
            model.Add(sum(self.indicators[team_index][0:self.advancing_team_count]) == 1).only_enforce_if(top_n)
            model.Add(sum(self.indicators[team_index][0:self.advancing_team_count]) == 0).only_enforce_if(top_n.Not())
            model.Add(sum(stage.indicators[team_index]) == 1).only_enforce_if(top_n)
            model.Add(sum(stage.indicators[team_index]) == 0).only_enforce_if(top_n.Not())


class PairGroupStage(Stage, ABC):
    def __init__(self,
                 name: str,
                 team_count_per_group: int,
                 advancing_team_count_per_group: int,
                 metadata: Metadata,
                 group_a: [Team] = None,
                 group_b: [Team] = None):
        if advancing_team_count_per_group > team_count_per_group:
            raise ValueError(f"Advancing team count {advancing_team_count_per_group} must be less than team count {team_count_per_group}")

        super().__init__(name, team_count_per_group * 2, metadata)
        self.advancing_team_count_per_group = advancing_team_count_per_group
        self.group_a = group_a
        self.group_b = group_b

    def add_team_constraints(self):
        # If we don't know groups, don't bother
        if self.group_a is None:
            return

        # By convention, assume A is odd, B is even
        # A finishes 1st, 3rd, 5th, etc.
        team_database = self.metadata.team_database
        model = self.metadata.model
        for team in self.group_a:
            team_index = team_database.get_team_index(team)
            row_sum = 0
            for placement in range(0, self.team_count, 2):
                row_sum += self.indicators[team_index][placement]
            model.Add(row_sum == 1)

        # B finishes 2nd, 4th, 6th, etc.
        for team in self.group_b:
            team_index = team_database.get_team_index(team)
            row_sum = 0
            for placement in range(1, self.team_count, 2):
                row_sum += self.indicators[team_index][placement]
            model.Add(row_sum == 1)

    def bind_forward(self, stage: "Stage"):
        model: CpModel = self.metadata.model

        # Top N teams make it through to the next Stage
        # They will place *somewhere* in the next Stage
        for team in self.metadata.team_database.get_all_teams():
            top_n: [BooleanVar] = model.new_bool_var(f"{self.name}_{team.name}_top_{self.advancing_team_count_per_group}")
            team_index: int = self.metadata.team_database.get_team_index(team)
            model.Add(sum(self.indicators[team_index][0:self.advancing_team_count_per_group]) == 1).only_enforce_if(top_n)
            model.Add(sum(self.indicators[team_index][0:self.advancing_team_count_per_group]) == 0).only_enforce_if(top_n.Not())
            model.Add(sum(stage.indicators[team_index]) == 1).only_enforce_if(top_n)
            model.Add(sum(stage.indicators[team_index]) == 0).only_enforce_if(top_n.Not())