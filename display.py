from typing import Dict

import pyperclip
from ortools.sat.python.cp_model import CpSolver

from display_phases import HasDisplayPhase, DisplayPhase, Placement
from ept import EptTournament
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

    def print(self, team_to_optimise: Team, top_n: int, max_points: float, solver: CpSolver):
        output: str = ""
        output += "==What does the threshold scenario look like?==\n"
        output += f"This is the following scenario where {{{{Team|{team_to_optimise.name}}}}} fail to finish in the <u>top {top_n}</u> with {round(max_points)} points.\n"
        output += '{| class="wikitable" style="font-size:85%; text-align: center;"\n'
        output += "! rowspan=\"2\" style=\"min-width:40px\" | '''Place'''\n"
        output += "! rowspan=\"2\" style=\"min-width:200px\" | '''Team'''\n"
        output += "! style=\"min-width:50px\" | '''Point'''\n"

        # Prep - evaluate all the tournaments/transfer windows and get their placements
        all_display_phases: [DisplayPhase] = []
        for tournament_or_transfer_window in self.tournaments_or_transfer_windows:
            all_display_phases.extend(tournament_or_transfer_window.to_display_phases(solver))
            if isinstance(tournament_or_transfer_window, EptTournament):
                ept_tournament: EptTournament = tournament_or_transfer_window
                output += f"! colspan=\"{ept_tournament.tournament.stage_count()}\" style=\"min-width:50px\" | {{{{LeagueIconSmall{ept_tournament.liquipedia_league_icon}|name={ept_tournament.liquipedia_display_name}|link={ept_tournament.liquipedia_link}|edate={ept_tournament.liquipedia_edate}}}}}\n"
            else:
                output += "! rowspan=\"2\" | <span title=\"Transfer window\">&hArr;</span>\n"

        output += "|-\n"
        output += f"! '''{(round(max_points) + 1)}'''\n"
        for tournament_or_transfer_window in self.tournaments_or_transfer_windows:
            if isinstance(tournament_or_transfer_window, EptTournament):
                ept_tournament: EptTournament = tournament_or_transfer_window
                output = self.display_phases_header(output, ept_tournament)
        output += "|-\n"

        total_points: Dict[Team, int] = {}
        for display_phase in all_display_phases:
            for points, placement in display_phase.placements.items():
                team = placement.team
                if team in total_points:
                    total_points[team] += placement.points
                else:
                    total_points[team] = placement.points

        sorted_total_points: Dict[Team, int] = dict(sorted(total_points.items(), key=lambda item: item[1], reverse=True))

        def formatted_points(p: Placement) -> str:
            return formatted_points_inner(p.place, p.points)

        def formatted_points_inner(place: int | None, pts: int | None) -> str:
            if pts is None or pts == 0:
                return f"{pts}"

            if place is None:
                return f"{pts}"

            if place > 3:
                return f"{pts}"

            return f"{{{{PlacementBg/{place + 1}}}}} {pts}"

        i = 0
        for team, total_points in sorted_total_points.items():
            output += "|-\n"
            output += f"| {(i + 1)}\n"
            output += f"|style=\"text-align: left;\"| {{{{Team|{team.name}}}}}\n"
            output += f"| {formatted_points_inner(i, total_points)}\n"
            for display_phase in all_display_phases:
                placement_for_team: Placement = display_phase.get_placement_for_team(team)
                output += f"| {formatted_points(placement_for_team)}\n"

            output += "|-\n"
            i += 1

        output += "|}"
        pyperclip.copy(output)
        print(output)
        print()

    @staticmethod
    def display_phases_header(output, tournament: EptTournament):
        stage_count = tournament.tournament.stage_count()
        if stage_count == 1:
            output += "! {{Abbr|Fin|Final position}}\n"
        elif stage_count == 2:
            output += "! GS || {{Abbr|Fin|Final position}}\n"
        elif stage_count == 3:
            output += "! GS1 || GS2 || {{Abbr|Fin|Final position}}\n"
        else:
            raise Exception(
                f"Unknown number of points scoring phases {stage_count}")
        return output
