from abc import ABC, abstractmethod

from ortools.constraint_solver.pywrapcp import BooleanVar
from ortools.sat.python.cp_model import CpModel, IntVar

from metadata import Metadata
from teams import Team, TeamDatabase


class TeamConstraint:
    def __init__(self, team: Team, lower: int, upper: int):
        self.team = team
        self.lower = lower
        self.upper = upper


class Tournament:
    def __init__(self,
                 name: str,
                 starting_stage: "Stage",
                 metadata: Metadata):
        self.name = name
        self.starting_stage = starting_stage
        self.metadata = metadata
        self.is_team_list_complete = False

        self.indicators: [[BooleanVar]] = [
            [self.metadata.model.new_bool_var(
                f'x_{self.name}_{self.metadata.team_database.get_team_by_index(i).name}_{j}') for j in
                range(self.starting_stage.team_count)]
            for i in range(len(self.metadata.team_database.get_all_teams()))]

    def build(self):
        # One placement per team
        model: CpModel = self.metadata.model

        # One team per place
        # This will not work if, say, two teams are invited to a later stage
        team_database = self.metadata.team_database
        all_teams = team_database.get_all_teams()
        for placement in range(self.starting_stage.team_count):
            model.Add(sum(self.indicators[i][placement] for i in range(
                len(all_teams))) == 1)

        # One place per team
        for team in all_teams:
            model.Add(sum(self.indicators[team_database.get_team_index(team)]) <= 1)

        next_stage: Stage = self.starting_stage
        while next_stage is not None:
            next_stage.bind_elimination(self)
            next_stage = next_stage.next_stage

    def stage_count(self) -> int:
        stages: int = 0
        next_stage: Stage = self.starting_stage
        while next_stage is not None:
            stages += 1
            next_stage = next_stage.next_stage
        return stages

    def mark_participating_teams_complete(self):
        self.is_team_list_complete = True

    def is_team_participating(self, team: Team) -> bool:
        return self.starting_stage.is_team_participating(team)


class Stage(ABC):
    def __init__(self,
                 name: str,
                 team_count: int,
                 metadata: Metadata):
        self.name = name
        self.team_count: int = team_count
        self.metadata: Metadata = metadata
        self.participating_teams_if_group_unknown = None

        self.indicators: [[BooleanVar]] = [
            [self.metadata.model.new_bool_var(
                f'x_{self.name}_{self.metadata.team_database.get_team_by_index(i).name}_{j}') for j in
                range(self.team_count)]
            for i in range(len(self.metadata.team_database.get_all_teams()))]

        self.next_stage: Stage | None = None
        self.team_constraints: [TeamConstraint] = []
        self.team_guaranteed_playoff_lb_or_eliminated: [Team] = []

    def build(self):
        # One placement per team
        model: CpModel = self.metadata.model
        for placement in range(self.team_count):
            model.Add(
                sum(self.indicators[i][placement] for i in
                    range(len(self.metadata.team_database.get_all_teams()))) == 1)

        for team_constraint in self.team_constraints:
            model.Add(sum(self.indicators[self.metadata.team_database.get_team_index(team_constraint.team)][i]
                          for i in range(team_constraint.lower, team_constraint.upper + 1)) == 1)

        model.Add(sum(self.indicators[self.metadata.team_database.get_team_index(team)][i]
                      for team in self.team_guaranteed_playoff_lb_or_eliminated for i in [0, 1]) <= 1)

        self.add_constraints()

    @abstractmethod
    def add_constraints(self):
        pass

    def bind_forward(self,
                     stage: "Stage"):
        self.next_stage = stage
        pass

    @abstractmethod
    def bind_elimination(self,
                         tournament: Tournament):
        pass

    @abstractmethod
    def is_team_participating(self, team: Team) -> bool:
        pass

    def team_can_finish_between(self, team_name: str, best: int, worst: int):
        team: Team = self.metadata.team_database.get_team_by_name(team_name)
        self.team_constraints.append(TeamConstraint(team, best - 1, worst - 1))

    def guaranteed_playoff_lb_or_eliminated(self, *team_names: str):
        self.team_guaranteed_playoff_lb_or_eliminated = self.metadata.team_database.get_teams_by_names(*team_names)

    def set_participating_teams(self, teams: [Team]):
        self.participating_teams_if_group_unknown = teams

class Root(Stage, ABC):
    def __init__(self,
                 name: str,
                 team_count: int,
                 metadata: Metadata,
                 teams: [Team]):
        super().__init__(name, team_count, metadata)
        self.teams = teams

    def add_constraints(self):
        model: CpModel = self.metadata.model

        # Every team here makes it through to the next Stage
        # They will place *somewhere* in the next Stage
        for team in self.teams:
            team_index: int = self.metadata.team_database.get_team_index(team)
            model.Add(sum(self.next_stage.indicators[team_index]) == 1)
        pass

    def bind_elimination(self, tournament: Tournament):
        raise Exception("Root is not intended to be a final position")

    def is_team_participating(self, team: Team) -> bool:
        return team in self.teams


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

    def add_constraints(self):
        model: CpModel = self.metadata.model

        # Top N teams make it through to the next Stage
        # They will place *somewhere* in the next Stage
        if self.next_stage is not None:
            for team in self.metadata.team_database.get_all_teams():
                top_n: IntVar = model.new_bool_var(f"{self.name}_{team.name}_top_{self.advancing_team_count}")
                team_index: int = self.metadata.team_database.get_team_index(team)
                model.Add(sum(self.indicators[team_index][0:self.advancing_team_count]) == 1).only_enforce_if(top_n)
                model.Add(sum(self.indicators[team_index][0:self.advancing_team_count]) == 0).only_enforce_if(
                    top_n.Not())
                model.Add(sum(self.next_stage.indicators[team_index]) == 1).only_enforce_if(top_n)
                model.Add(sum(self.next_stage.indicators[team_index]) == 0).only_enforce_if(top_n.Not())

    def bind_elimination(self, tournament: Tournament):
        super().bind_elimination(tournament)

        model: CpModel = self.metadata.model

        # Teams not in the top N have a final placement
        team_database = self.metadata.team_database
        for team in team_database.get_all_teams():
            team_index = team_database.get_team_index(team)
            for p in range(self.advancing_team_count, self.team_count):
                model.Add(self.indicators[team_index][p] == tournament.indicators[team_index][p])
        pass

    def is_team_participating(self, team: Team) -> bool:
        # TODO: This is unaware of the teams taking part, because it's never used as a root.  Need to find a way to do this
        return True


class PairGroupStage(Stage, ABC):
    def __init__(self,
                 name: str,
                 team_count_per_group: int,
                 advancing_team_count_per_group: int,
                 metadata: Metadata,
                 group_a: [Team] = None,
                 group_b: [Team] = None):
        if advancing_team_count_per_group > team_count_per_group:
            raise ValueError(
                f"Advancing team count {advancing_team_count_per_group} must be less than team count {team_count_per_group}")

        super().__init__(name, team_count_per_group * 2, metadata)
        self.advancing_team_count_per_group = advancing_team_count_per_group
        self.group_a = group_a
        self.group_b = group_b

    def add_constraints(self):
        team_database: TeamDatabase = self.metadata.team_database
        model: CpModel = self.metadata.model

        # By convention, assume A is odd, B is even
        # A finishes 1st, 3rd, 5th, etc.
        if self.group_a is not None:
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

        # Top N teams make it through to the next Stage
        # They will place *somewhere* in the next Stage
        # Remember, 2 group stages
        if self.next_stage is not None:
            for team in self.metadata.team_database.get_all_teams():
                top_n: [BooleanVar] = model.new_bool_var(
                    f"{self.name}_{team.name}_top_{self.advancing_team_count_per_group}")
                team_index: int = self.metadata.team_database.get_team_index(team)
                model.Add(
                    sum(self.indicators[team_index][0:self.advancing_team_count_per_group * 2]) == 1).only_enforce_if(
                    top_n)
                model.Add(
                    sum(self.indicators[team_index][0:self.advancing_team_count_per_group * 2]) == 0).only_enforce_if(
                    top_n.Not())
                model.Add(sum(self.next_stage.indicators[team_index]) == 1).only_enforce_if(top_n)
                model.Add(sum(self.next_stage.indicators[team_index]) == 0).only_enforce_if(top_n.Not())

    def bind_elimination(self, tournament: Tournament):
        super().bind_elimination(tournament)

        model: CpModel = self.metadata.model

        # Teams not in the top N have a final placement
        # Remember, two group stages
        team_database = self.metadata.team_database
        for team in team_database.get_all_teams():
            team_index = team_database.get_team_index(team)
            for p in range(self.advancing_team_count_per_group * 2, self.team_count):
                model.Add(self.indicators[team_index][p] == tournament.indicators[team_index][p])
        pass

    def is_team_participating(self, team: Team) -> bool:
        # This is weird but it is called by the optimiser to see if a team can actually meet the threshold or not
        # If we do not know concrete groups, it is better to say "yes" so the optimiser is forced to go through it
        if self.group_a is not None:
            return team in self.group_a or team in self.group_b

        if self.participating_teams_if_group_unknown is not None:
            return team in self.participating_teams_if_group_unknown

        return True


class SingleMatch(Stage, ABC):
    def __init__(self, name: str, metadata: Metadata, teams: [Team] = None):
        super().__init__(name, 2, metadata)
        self.name = name
        self.metadata = metadata
        self.team_a = None
        self.team_b = None

        if teams is not None:
            if len(teams) != 2:
                raise ValueError(f"Only two teams (not {len(teams)}) expected")

            self.team_a = teams[0]
            self.team_b = teams[1]

    def add_constraints(self):
        if self.team_a is not None:
            database: TeamDatabase = self.metadata.team_database
            model: CpModel = self.metadata.model
            model.Add(sum(self.indicators[database.get_team_index(self.team_a)]) == 1)
            model.Add(sum(self.indicators[database.get_team_index(self.team_b)]) == 1)

    def bind_winner(self, next_match: "SingleMatch"):
        for team in self.metadata.team_database.get_all_teams():
            model: CpModel = self.metadata.model
            team_index: int = self.metadata.team_database.get_team_index(team)

            is_in_this_match: [BooleanVar] = model.new_bool_var(f"{self.name}_{team.name}_is_in_this_match")
            winner: [BooleanVar] = model.new_bool_var(f"{self.name}_{team.name}_winner")

            model.Add(sum(self.indicators[team_index]) == 1).only_enforce_if(is_in_this_match)
            model.Add(sum(self.indicators[team_index]) == 0).only_enforce_if(is_in_this_match.Not())

            model.Add(self.indicators[team_index][0] == 1).only_enforce_if(winner)
            model.Add(self.indicators[team_index][0] == 0).only_enforce_if(winner.Not())

            is_in_this_match_and_advancing: [BooleanVar] = model.new_bool_var(
                f"{self.name}_{team.name}_is_in_this_match_and_advancing")
            model.AddBoolAnd([is_in_this_match, winner]).only_enforce_if(is_in_this_match_and_advancing)
            model.AddBoolOr([is_in_this_match.Not(), winner.Not()]).only_enforce_if(
                is_in_this_match_and_advancing.Not())

            is_in_this_match_and_eliminated: [BooleanVar] = model.new_bool_var(
                f"{self.name}_{team.name}_is_in_this_match_and_eliminated")
            model.AddBoolAnd([is_in_this_match, winner.Not()]).only_enforce_if(is_in_this_match_and_eliminated)
            model.AddBoolOr([is_in_this_match.Not(), winner]).only_enforce_if(
                is_in_this_match_and_eliminated.Not())

            model.Add(sum(next_match.indicators[team_index]) == 1).only_enforce_if(is_in_this_match_and_advancing)

    def bind_loser(self, next_match: "SingleMatch"):
        for team in self.metadata.team_database.get_all_teams():
            model: CpModel = self.metadata.model
            team_index: int = self.metadata.team_database.get_team_index(team)

            is_in_this_match: [BooleanVar] = model.new_bool_var(f"{self.name}_{team.name}_is_in_this_match")
            loser: [BooleanVar] = model.new_bool_var(f"{self.name}_{team.name}_loser")

            model.Add(sum(self.indicators[team_index]) == 1).only_enforce_if(is_in_this_match)
            model.Add(sum(self.indicators[team_index]) == 0).only_enforce_if(is_in_this_match.Not())

            model.Add(self.indicators[team_index][1] == 1).only_enforce_if(loser)
            model.Add(self.indicators[team_index][1] == 0).only_enforce_if(loser.Not())

            is_in_this_match_and_advancing: [BooleanVar] = model.new_bool_var(
                f"{self.name}_{team.name}_is_in_this_match_and_advancing")
            model.AddBoolAnd([is_in_this_match, loser]).only_enforce_if(is_in_this_match_and_advancing)
            model.AddBoolOr([is_in_this_match.Not(), loser.Not()]).only_enforce_if(
                is_in_this_match_and_advancing.Not())

            is_in_this_match_and_eliminated: [BooleanVar] = model.new_bool_var(
                f"{self.name}_{team.name}_is_in_this_match_and_eliminated")
            model.AddBoolAnd([is_in_this_match, loser.Not()]).only_enforce_if(is_in_this_match_and_eliminated)
            model.AddBoolOr([is_in_this_match.Not(), loser]).only_enforce_if(
                is_in_this_match_and_eliminated.Not())

            model.Add(sum(next_match.indicators[team_index]) == 1).only_enforce_if(is_in_this_match_and_advancing)

    def bind_qualification(self, first_stage: Stage):
        for team in self.metadata.team_database.get_all_teams():
            model: CpModel = self.metadata.model
            team_index: int = self.metadata.team_database.get_team_index(team)

            is_in_this_match: [BooleanVar] = model.new_bool_var(f"{self.name}_{team.name}_is_in_this_match")
            winner: [BooleanVar] = model.new_bool_var(f"{self.name}_{team.name}_winner")

            model.Add(sum(self.indicators[team_index]) == 1).only_enforce_if(is_in_this_match)
            model.Add(sum(self.indicators[team_index]) == 0).only_enforce_if(is_in_this_match.Not())

            model.Add(self.indicators[team_index][0] == 1).only_enforce_if(winner)
            model.Add(self.indicators[team_index][0] == 0).only_enforce_if(winner.Not())

            is_in_this_match_and_advancing: [BooleanVar] = model.new_bool_var(
                f"{self.name}_{team.name}_is_in_this_match_and_advancing")
            model.AddBoolAnd([is_in_this_match, winner]).only_enforce_if(is_in_this_match_and_advancing)
            model.AddBoolOr([is_in_this_match.Not(), winner.Not()]).only_enforce_if(
                is_in_this_match_and_advancing.Not())

            is_in_this_match_and_eliminated: [BooleanVar] = model.new_bool_var(
                f"{self.name}_{team.name}_is_in_this_match_and_eliminated")
            model.AddBoolAnd([is_in_this_match, winner.Not()]).only_enforce_if(is_in_this_match_and_eliminated)
            model.AddBoolOr([is_in_this_match.Not(), winner]).only_enforce_if(
                is_in_this_match_and_eliminated.Not())

            model.Add(sum(first_stage.indicators[team_index]) == 1).only_enforce_if(is_in_this_match_and_advancing)
            model.Add(sum(first_stage.indicators[team_index]) == 0).only_enforce_if(is_in_this_match_and_eliminated)

    def bind_elimination(self, tournament: Tournament):
        pass

    def is_team_participating(self, team: Team) -> bool:
        return team == self.team_a or team == self.team_b

    def set_winner(self, team_name: str):
        metadata = self.metadata
        metadata.model.Add(self.indicators[metadata.team_database.get_team_index_by_team_name(team_name)][0] == 1)


# noinspection PyPep8Naming
class DoubleElimination_8U1Q(Stage, ABC):
    def __init__(self, name: str, teams: [Team], metadata: Metadata):
        super().__init__(name, 8, metadata)

        self.teams = teams

        # Bracket
        self.ubqf_1: SingleMatch = SingleMatch(f"{name}_ubqf_1", metadata, teams[0:2])
        self.ubqf_2: SingleMatch = SingleMatch(f"{name}_ubqf_2", metadata, teams[2:4])
        self.ubqf_3: SingleMatch = SingleMatch(f"{name}_ubqf_3", metadata, teams[4:6])
        self.ubqf_4: SingleMatch = SingleMatch(f"{name}_ubqf_4", metadata, teams[6:8])

        self.ubsf_1: SingleMatch = SingleMatch(f"{name}_ubsf_1", metadata)
        self.ubsf_2: SingleMatch = SingleMatch(f"{name}_ubsf_2", metadata)

        self.ubf: SingleMatch = SingleMatch(f"{name}_ubf", metadata)

        self.lbr1_1: SingleMatch = SingleMatch(f"{name}_lbr1_1", metadata)
        self.lbr1_2: SingleMatch = SingleMatch(f"{name}_lbr1_2", metadata)

        self.lbr2_1: SingleMatch = SingleMatch(f"{name}_lbr2_1", metadata)
        self.lbr2_2: SingleMatch = SingleMatch(f"{name}_lbr2_2", metadata)

        self.lbsf: SingleMatch = SingleMatch(f"{name}_lbsf", metadata)

        self.lbf: SingleMatch = SingleMatch(f"{name}_lbf", metadata)

        self.gf: SingleMatch = SingleMatch(f"{name}_gf", metadata)

        self.ubqf_1.bind_winner(self.ubsf_1)
        self.ubqf_1.bind_loser(self.lbr1_1)
        self.ubqf_2.bind_winner(self.ubsf_1)
        self.ubqf_2.bind_loser(self.lbr1_1)
        self.ubqf_3.bind_winner(self.ubsf_2)
        self.ubqf_3.bind_loser(self.lbr1_2)
        self.ubqf_4.bind_winner(self.ubsf_2)
        self.ubqf_4.bind_loser(self.lbr1_2)

        self.ubsf_1.bind_winner(self.ubf)
        self.ubsf_1.bind_loser(self.lbr2_2)
        self.ubsf_2.bind_winner(self.ubf)
        self.ubsf_2.bind_loser(self.lbr2_1)

        self.ubf.bind_winner(self.gf)
        self.ubf.bind_loser(self.lbf)

        self.lbr1_1.bind_winner(self.lbr2_1)
        self.lbr1_2.bind_winner(self.lbr2_2)

        self.lbr2_1.bind_winner(self.lbsf)
        self.lbr2_2.bind_winner(self.lbsf)

        self.lbsf.bind_winner(self.lbf)

        self.lbf.bind_winner(self.gf)

        self.ubqf_1.build()
        self.ubqf_2.build()
        self.ubqf_3.build()
        self.ubqf_4.build()

        self.ubsf_1.build()
        self.ubsf_2.build()

        self.ubf.build()

        self.lbr1_1.build()
        self.lbr1_2.build()

        self.lbr2_1.build()
        self.lbr2_2.build()

        self.lbsf.build()

        self.lbf.build()

        self.gf.build()

    def is_team_participating(self, team: Team) -> bool:
        return team in self.teams


# noinspection PyPep8Naming
class DoubleElimination_2U2L1D(Stage, ABC):
    def __init__(self, name: str, metadata: Metadata):
        super().__init__(name, 4, metadata)

        # Bracket
        self.ubf: SingleMatch = SingleMatch(f"{name}_ubf", metadata)
        self.lbsf: SingleMatch = SingleMatch(f"{name}_lbsf", metadata)
        self.lbf: SingleMatch = SingleMatch(f"{name}_lbf", metadata)
        self.gf: SingleMatch = SingleMatch(f"{name}_gf", metadata)

        self.ubf.bind_winner(self.gf)
        self.ubf.bind_loser(self.lbf)

        self.lbsf.bind_winner(self.lbf)

        self.lbf.bind_winner(self.gf)

        self.ubf.build()
        self.lbsf.build()
        self.lbf.build()
        self.gf.build()

    def add_constraints(self):
        pass

    def bind_backward(self, previous_stage: "Stage"):
        team_database = self.metadata.team_database
        model = self.metadata.model

        for team in team_database.get_all_teams():
            team_index: int = team_database.get_team_index(team)

            model.Add(sum(previous_stage.indicators[team_index][0:2]) == sum(self.ubf.indicators[team_index][0:2]))
            model.Add(sum(previous_stage.indicators[team_index][2:4]) == sum(self.lbsf.indicators[team_index][0:2]))

    def bind_elimination(self, tournament: Tournament):
        model: CpModel = self.metadata.model
        team_database: TeamDatabase = self.metadata.team_database

        for team in team_database.get_all_teams():
            team_index: int = team_database.get_team_index(team)
            model.Add(self.gf.indicators[team_index][0] == tournament.indicators[team_index][0])
            model.Add(self.gf.indicators[team_index][1] == tournament.indicators[team_index][1])
            model.Add(self.lbf.indicators[team_index][1] == tournament.indicators[team_index][2])
            model.Add(self.lbsf.indicators[team_index][1] == tournament.indicators[team_index][3])

    def is_team_participating(self, team: Team) -> bool:
        # TODO: Is not used as root, so teams are unknown
        return True


# noinspection PyPep8Naming
class DoubleElimination_4U4L2DSL1D(Stage, ABC):
    def __init__(self, name: str, metadata: Metadata, previous_stage_lbr1_1_positions=None):
        super().__init__(name, 8, metadata)

        # For some reason, this is not A5 vs. B6 and B5 vs. A6, but can be A5 vs. B5 (ESL One Bangkok 2024)
        # This field defines what LBR1 series 1 (in Liquipedia terms) positions should be.
        # A3=4, B3=5, A4=6, B6=7
        if previous_stage_lbr1_1_positions is None:
            previous_stage_lbr1_1_positions = [4, 7]
        self.previous_stage_lbr1_1_positions = previous_stage_lbr1_1_positions

        # Bracket
        self.ubsf_1: SingleMatch = SingleMatch(f"{name}_ubsf_1", metadata)
        self.ubsf_2: SingleMatch = SingleMatch(f"{name}_ubsf_2", metadata)
        self.ubf: SingleMatch = SingleMatch(f"{name}_ubf", metadata)
        self.gf: SingleMatch = SingleMatch(f"{name}_gf", metadata)

        self.lbr1_1: SingleMatch = SingleMatch(f"{name}_lbr1_1", metadata)
        self.lbr1_2: SingleMatch = SingleMatch(f"{name}_lbr1_2", metadata)
        self.lbqf_1: SingleMatch = SingleMatch(f"{name}_lbqf_1", metadata)
        self.lbqf_2: SingleMatch = SingleMatch(f"{name}_lbqf_2", metadata)
        self.lbsf: SingleMatch = SingleMatch(f"{name}_lbsf", metadata)
        self.lbf: SingleMatch = SingleMatch(f"{name}_lbf", metadata)

        self.ubsf_1.bind_winner(self.ubf)
        self.ubsf_1.bind_loser(self.lbqf_1)
        self.ubsf_2.bind_winner(self.ubf)
        self.ubsf_2.bind_loser(self.lbqf_2)

        self.ubf.bind_winner(self.gf)
        self.ubf.bind_loser(self.lbf)

        self.lbr1_1.bind_winner(self.lbqf_1)
        self.lbr1_2.bind_winner(self.lbqf_2)

        self.lbqf_1.bind_winner(self.lbsf)
        self.lbqf_2.bind_winner(self.lbsf)

        self.lbsf.bind_winner(self.lbf)

        self.lbf.bind_winner(self.gf)

        self.ubsf_1.build()
        self.ubsf_2.build()
        self.ubf.build()
        self.lbr1_1.build()
        self.lbr1_2.build()
        self.lbqf_1.build()
        self.lbqf_2.build()
        self.lbsf.build()
        self.lbf.build()
        self.gf.build()

    def add_constraints(self):
        pass

    def bind_backward(self, previous_stage: "Stage"):
        team_database = self.metadata.team_database
        model = self.metadata.model

        for team in team_database.get_all_teams():
            team_index: int = team_database.get_team_index(team)

            model.Add(previous_stage.indicators[team_index][0] + previous_stage.indicators[team_index][3] == sum(
                self.ubsf_1.indicators[team_index][0:2]))
            model.Add(previous_stage.indicators[team_index][1] + previous_stage.indicators[team_index][2] == sum(
                self.ubsf_2.indicators[team_index][0:2]))

            lbr1_2_matchups = list({4, 5, 6, 7} - set(self.previous_stage_lbr1_1_positions))
            lbr1_1_sum = 0
            for lbr1_1_prev in self.previous_stage_lbr1_1_positions:
                lbr1_1_sum = lbr1_1_sum + previous_stage.indicators[team_index][lbr1_1_prev]
            model.Add(lbr1_1_sum == sum(self.lbr1_1.indicators[team_index][0:2]))

            lbr1_2_sum = 0
            for lbr1_2_prev in lbr1_2_matchups:
                lbr1_2_sum = lbr1_2_sum + previous_stage.indicators[team_index][lbr1_2_prev]
            model.Add(lbr1_2_sum == sum(self.lbr1_2.indicators[team_index][0:2]))

    def bind_elimination(self, tournament: Tournament):
        model: CpModel = self.metadata.model
        team_database: TeamDatabase = self.metadata.team_database

        for team in team_database.get_all_teams():
            team_index: int = team_database.get_team_index(team)
            model.Add(self.gf.indicators[team_index][0] == tournament.indicators[team_index][0])
            model.Add(self.gf.indicators[team_index][1] == tournament.indicators[team_index][1])
            model.Add(self.lbf.indicators[team_index][1] == tournament.indicators[team_index][2])
            model.Add(self.lbsf.indicators[team_index][1] == tournament.indicators[team_index][3])
            model.Add(self.lbqf_1.indicators[team_index][1] == tournament.indicators[team_index][4])
            model.Add(self.lbqf_2.indicators[team_index][1] == tournament.indicators[team_index][5])
            model.Add(self.lbr1_1.indicators[team_index][1] == tournament.indicators[team_index][6])
            model.Add(self.lbr1_2.indicators[team_index][1] == tournament.indicators[team_index][7])

    def is_team_participating(self, team: Team) -> bool:
        # TODO: is not used as root, so teams are unknown
        return True
