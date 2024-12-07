from math import log10, floor

from ortools.constraint_solver.pywrapcp import BooleanVar
from ortools.sat.python.cp_model import CpSolver

from teams import TeamDatabase, Team


def print_indicators(indicators: [[BooleanVar]], solver: CpSolver, team_database: TeamDatabase):
    if indicators is None or len(indicators) == 0:
        return

    pad_placement: int = floor(log10(len(indicators)))
    pad_team: int = max([len(team.name) for team in team_database.get_all_teams()])
    for row in range(len(indicators)):
        team: Team = team_database.get_team_by_index(row)
        print(f"{team.name.rjust(pad_team, " ")}", end="")
        row_sum = 0
        for cell in indicators[row]:
            value = solver.value(cell)
            row_sum += value
            print(f" {str(int(value)).zfill(pad_placement)}", end="")
        if row_sum == 1:
            print(" Q")
        else:
            print(" NQ")
    print()