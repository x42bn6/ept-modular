from typing import Dict

from ortools.sat.python.cp_model import CpSolver

from display_phases import HasDisplayPhase, DisplayPhase
from metadata import Metadata
from teams import Team

class DisplayRow:
    def __init__(self, team: Team, total_points: int):
        self.team = team
        self.total_points = total_points

class Display:
    def __init__(self, tournaments_or_transfer_windows: [HasDisplayPhase], metadata: Metadata):
        self.tournaments_or_transfer_windows: [HasDisplayPhase] = tournaments_or_transfer_windows
        self.metadata = metadata

    def print(self, solver: CpSolver):
        # Prep - evaluate all the tournaments/transfer windows and get their placements
        all_display_phases: [DisplayPhase] = []
        for tournament_or_transfer_window in self.tournaments_or_transfer_windows:
            all_display_phases.extend(tournament_or_transfer_window.to_display_phases(solver))

        total_points: Dict[Team, int] = {}
        for display_phase in all_display_phases:
            for points, placement in display_phase.placements.items():
                team = placement.team
                if team in total_points:
                    total_points[team] += points
                else:
                    total_points[team] = points

        sorted_total_points: Dict[Team, int] = dict(sorted(total_points.items(), key=lambda item: item[1]))

        for team, total_points in sorted_total_points.items():
            print(f"{team.name} -- {total_points}", end="")
            for display_phase in all_display_phases:
                phase_placement = display_phase.get_placement_for_team(team)
                print(f"-- {display_phase.name}={phase_placement}", end="")
            print()

        print()
