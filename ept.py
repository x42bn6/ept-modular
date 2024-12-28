from abc import ABC, abstractmethod
from array import array
from math import floor
from typing import Dict

from ortools.sat.python.cp_model import IntVar, CpSolver

from display_phases import DisplayPhase, HasDisplayPhase, DisplayPhaseType
from metadata import Metadata
from stage import GroupStage, Stage, Tournament, PairGroupStage
from teams import Team


class EptStage:
    def __init__(self,
                 stage: Stage,
                 points: [int]):
        if len(points) > stage.team_count:
            raise ValueError(f"Cannot assign more points {points} than team count {stage.team_count}")

        self.stage = stage
        self.points = [points[p] if p < len(points) else 0 for p in range(stage.team_count)]
        self.build()

        self.next_ept_stage = None
        self.obtained_points: [IntVar] = []

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def get_points(self) -> [IntVar]:
        pass

    def bind_next_ept_stage(self, next_ept_stage: "EptStage"):
        self.next_ept_stage = next_ept_stage

    def to_display_phase(self, solver: CpSolver) -> DisplayPhase:
        team_database = self.stage.metadata.team_database
        point_map: Dict[int, array[Team]] = {}
        for team in team_database.get_all_teams():
            team_index: int = team_database.get_team_index(team)
            points: int = solver.value(self.obtained_points[team_index])
            if points in point_map:
                point_map[points].append(team)
            else:
                point_map[points] = [team]

        sorted_point_map: Dict[int, array[Team]] = dict(sorted(point_map.items(), reverse=True))
        display_phase: DisplayPhase = DisplayPhase(self.stage.name, self.stage.team_count, DisplayPhaseType.TOURNAMENT)
        placement = 0
        for points, team_array in sorted_point_map.items():
            for team in team_array:
                display_phase.add_placement(team, placement, points)
                placement += 1

        return display_phase


class EptGroupStage(EptStage, ABC):
    def __init__(self,
                 stage: GroupStage,
                 points: [int]):
        super().__init__(stage, points)
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


class EptTournament(HasDisplayPhase, ABC):
    def __init__(self,
                 tournament: Tournament,
                 first_ept_stage: EptStage,
                 points: [int],
                 liquipedia_display_name: str,
                 liquipedia_link: str,
                 liquipedia_league_icon: str,
                 liquipedia_edate: str,
                 metadata: Metadata):
        super().__init__()
        self.tournament = tournament
        self.first_ept_stage = first_ept_stage
        self.points = points
        self.liquipedia_display_name = liquipedia_display_name
        self.liquipedia_link = liquipedia_link
        self.liquipedia_league_icon = liquipedia_league_icon
        self.liquipedia_edate = liquipedia_edate
        self.metadata = metadata
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

    def to_display_phases(self, solver: CpSolver) -> [DisplayPhase]:
        display_phases: [DisplayPhase] = []
        next_ept_stage: EptStage = self.first_ept_stage
        while next_ept_stage is not None:
            display_phases.append(next_ept_stage.to_display_phase(solver))
            next_ept_stage = next_ept_stage.next_ept_stage

        # Tournament itself has points
        team_database = self.metadata.team_database
        point_map: Dict[int, array[Team]] = {}
        for team in team_database.get_all_teams():
            team_index: int = team_database.get_team_index(team)
            points: int = solver.value(self.obtained_points[team_index])
            if points in point_map:
                point_map[points].append(team)
            else:
                point_map[points] = [team]

        sorted_point_map: Dict[int, array[Team]] = dict(sorted(point_map.items(), reverse=True))
        tournament_display_phase: DisplayPhase = DisplayPhase(self.tournament.name, len(self.points), DisplayPhaseType.TOURNAMENT)
        placement = 0
        for points, team_array in sorted_point_map.items():
            for team in team_array:
                tournament_display_phase.add_placement(team, placement, points)
                placement += 1
        display_phases.append(tournament_display_phase)

        return display_phases