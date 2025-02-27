from abc import ABC, abstractmethod
from array import array
from math import floor
from typing import Dict

from ortools.sat.python.cp_model import IntVar, CpSolver

from display_phases import DisplayPhase, HasDisplayPhase, DisplayPhaseType
from metadata import Metadata
from stage import GroupStage, Stage, Tournament, PairGroupStage
from teams import Team, TeamDatabase


class EptStageBase(ABC):
    def __init__(self, team_count: int, points: [int]):
        self.points = [points[p] if p < len(points) else 0 for p in range(team_count)]
        self.team_count = team_count
        self.next_ept_stage = None

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def to_display_phase(self, solver: CpSolver) -> DisplayPhase:
        pass

    def bind_next_ept_stage(self, next_ept_stage: "EptStageBase"):
        self.next_ept_stage = next_ept_stage

    @abstractmethod
    def get_obtained_points(self, team_index: int):
        pass


class EptStage(EptStageBase, ABC):
    def __init__(self, stage: Stage, points: [int]):
        if len(points) > stage.team_count:
            raise ValueError(f"Cannot assign more points {points} than team count {stage.team_count}")

        self.stage = stage

        super().__init__(stage.team_count, points)
        self.build()

        self.next_ept_stage = None
        self.obtained_points: [IntVar] = []

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def get_points(self) -> [IntVar]:
        pass

    def get_obtained_points(self, team_index: int):
        return self.obtained_points[team_index]

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


class SolvedEptStage(EptStageBase, ABC):
    def __init__(self, name: str, team_count: int, points: [int], metadata: Metadata):
        super().__init__(team_count, points)
        self.name = name
        self.team_database: TeamDatabase = metadata.team_database
        self.positions: Dict[Team, int] = {}

    def set_position(self, team_name: str, position: int):
        self.positions[self.team_database.get_team_by_name(team_name)] = position - 1

    def build(self):
        pass

    def to_display_phase(self, solver: CpSolver) -> DisplayPhase:
        team_database = self.team_database
        point_map: Dict[int, array[Team]] = {}
        for team in team_database.get_all_teams():
            points: int | None = None
            if team in self.positions:
                points = self.points[self.positions[team]]
            else:
                continue

            if points in point_map:
                point_map[points].append(team)
            else:
                point_map[points] = [team]

        sorted_point_map: Dict[int, array[Team]] = dict(sorted(point_map.items(), reverse=True))
        display_phase: DisplayPhase = DisplayPhase(self.name, self.team_count, DisplayPhaseType.TOURNAMENT)
        placement = 0
        for points, team_array in sorted_point_map.items():
            for team in team_array:
                display_phase.add_placement(team, placement, points)
                placement += 1

        return display_phase

    def bind_next_ept_stage(self, next_ept_stage: "EptStageBase"):
        super().bind_next_ept_stage(next_ept_stage)

    def get_obtained_points(self, team_index: int):
        team: Team = self.team_database.get_team_by_index(team_index)
        if team in self.positions:
            return self.points[self.positions[team]]
        return 0


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


class EptTournamentBase(HasDisplayPhase, ABC):
    def __init__(self,
                 points: [int],
                 first_ept_stage: EptStageBase,
                 liquipedia_display_name: str,
                 liquipedia_link: str,
                 liquipedia_league_icon: str,
                 liquipedia_edate: str,
                 metadata: Metadata):
        super().__init__()
        self.first_ept_stage = first_ept_stage
        self.liquipedia_display_name = liquipedia_display_name
        self.liquipedia_link = liquipedia_link
        self.liquipedia_league_icon = liquipedia_league_icon
        self.liquipedia_edate = liquipedia_edate
        self.points = points
        self.metadata = metadata

    @abstractmethod
    def to_display_phases(self, solver: CpSolver) -> [DisplayPhase]:
        pass

    @abstractmethod
    def is_complete(self) -> bool:
        pass

    @abstractmethod
    def get_maximum_points_for_team(self, team: Team) -> int | None:
        pass

    @abstractmethod
    def get_obtained_points(self, team_index: int) -> IntVar:
        pass

    def get_stage_count(self):
        count: int = 1
        next_ept_stage: EptStageBase = self.first_ept_stage
        while next_ept_stage is not None:
            count += 1
            next_ept_stage = next_ept_stage.next_ept_stage
        return count


class EptTournament(EptTournamentBase, HasDisplayPhase, ABC):
    def __init__(self,
                 tournament: Tournament,
                 first_ept_stage: EptStage,
                 points: [int],
                 liquipedia_display_name: str,
                 liquipedia_link: str,
                 liquipedia_league_icon: str,
                 liquipedia_edate: str,
                 metadata: Metadata):
        super().__init__(points,
                         first_ept_stage,
                         liquipedia_display_name,
                         liquipedia_link,
                         liquipedia_league_icon,
                         liquipedia_edate,
                         metadata)
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
        metadata: Metadata = self.metadata
        team_database = metadata.team_database
        self.obtained_points: [IntVar] = [metadata.model.new_int_var(0, 99999, f'd_{self.tournament.name}_{i}')
                                          for i in range(len(team_database.get_all_teams()))]
        for team in team_database.get_all_teams():
            team_index: int = team_database.get_team_index(team)
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
        tournament_display_phase: DisplayPhase = DisplayPhase(self.tournament.name, len(self.points),
                                                              DisplayPhaseType.TOURNAMENT)
        placement = 0
        for points, team_array in sorted_point_map.items():
            for team in team_array:
                tournament_display_phase.add_placement(team, placement, points)
                placement += 1
        display_phases.append(tournament_display_phase)

        return display_phases

    def is_complete(self) -> bool:
        return False

    def get_maximum_points_for_team(self, team: Team) -> int | None:
        if not self.tournament.is_team_participating(team):
            return 0

        max_points: int = self.points[0]
        next_ept_stage: EptStage = self.first_ept_stage
        while next_ept_stage is not None:
            max_points += next_ept_stage.points[0]
            next_ept_stage = next_ept_stage.next_ept_stage

        return max_points

    def get_obtained_points(self, team_index: int) -> [IntVar]:
        return self.obtained_points[team_index]


class SolvedEptTournament(EptTournamentBase, HasDisplayPhase, ABC):
    def __init__(self,
                 name: str,
                 first_ept_stage: SolvedEptStage,
                 points: [int],
                 liquipedia_display_name: str,
                 liquipedia_link: str,
                 liquipedia_league_icon: str,
                 liquipedia_edate: str,
                 metadata: Metadata):
        super().__init__(points,
                         first_ept_stage,
                         liquipedia_display_name,
                         liquipedia_link,
                         liquipedia_league_icon,
                         liquipedia_edate,
                         metadata)
        self.name = name
        self.first_ept_stage = first_ept_stage
        self.team_database: TeamDatabase = metadata.team_database
        self.positions: Dict[Team, int] = {}

    def set_position(self, team_name: str, position: int):
        self.positions[self.team_database.get_team_by_name(team_name)] = position - 1

    def to_display_phases(self, solver: CpSolver) -> [DisplayPhase]:
        display_phases: [DisplayPhase] = []
        next_ept_stage: SolvedEptStage = self.first_ept_stage
        while next_ept_stage is not None:
            display_phases.append(next_ept_stage.to_display_phase(solver))
            next_ept_stage = next_ept_stage.next_ept_stage

        # Tournament itself has points
        team_database = self.metadata.team_database
        point_map: Dict[int, array[Team]] = {}
        for team in team_database.get_all_teams():
            points: int = 0
            if team in self.positions:
                points: int = self.points[self.positions[team]]
            else:
                continue

            if points in point_map:
                point_map[points].append(team)
            else:
                point_map[points] = [team]

        sorted_point_map: Dict[int, array[Team]] = dict(sorted(point_map.items(), reverse=True))
        tournament_display_phase: DisplayPhase = DisplayPhase(self.name, len(self.points),
                                                              DisplayPhaseType.TOURNAMENT)
        placement = 0
        for points, team_array in sorted_point_map.items():
            for team in team_array:
                tournament_display_phase.add_placement(team, placement, points)
                placement += 1
        display_phases.append(tournament_display_phase)

        return display_phases

    def is_complete(self) -> bool:
        return True

    def get_maximum_points_for_team(self, team: Team) -> int | None:
        pass

    def get_obtained_points(self, team_index: int):
        team: Team = self.team_database.get_team_by_index(team_index)
        if team in self.positions:
            return self.points[self.positions[team]]
        return 0


