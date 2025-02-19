from ortools.constraint_solver.pywrapcp import BooleanVar
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, CpSolver, IntVar

from display import Display
from metadata import Metadata
from stage import SingleMatch
from teams import Team, Region, TeamDatabase
from tournaments.dreamleague_season_24 import DreamLeagueSeason24
from tournaments.esl_one_bangkok_2024 import EslOneBangkok2024


def main():
    teams: [Team] = [
        Team("Team Liquid", Region.WEU),
        Team("Gaimin Gladiators", Region.WEU),
        Team("Tundra Esports", Region.WEU),
        Team("AVULUS", Region.WEU),
        Team("Palianytsia", Region.WEU),

        Team("BetBoom Team", Region.EEU),
        Team("PARIVISION", Region.EEU),
        Team("Team Spirit", Region.EEU),
        Team("Natus Vincere", Region.EEU),

        Team("Team Falcons", Region.MESWA),
        Team("Nigma Galaxy", Region.MESWA),

        Team("Nouns Esports", Region.NA),
        Team("Shopify Rebellion", Region.NA),

        Team("HEROIC", Region.SA),
        Team("Team Waska", Region.SA),
        Team("beastcoast", Region.SA),

        Team("Xtreme Gaming", Region.CN),
        Team("Azure Ray", Region.CN),
        Team("Gaozu", Region.CN),

        Team("Talon Esports", Region.SEA),
        Team("BOOM Esports", Region.SEA),
    ]
    team_database: TeamDatabase = TeamDatabase()
    for team in teams:
        team_database.add_team(team)

    max_objective_value = -1
    for team in team_database.get_all_teams():
        model: CpModel = CpModel()
        metadata: [Metadata] = Metadata(team_database, model)

        ept_dl_s24, ept_dl_s24_gs1, ept_dl_s24_gs2 = DreamLeagueSeason24(metadata).build()
        ept_esl_one_bkk, ept_esl_one_bkk_2024_gs = EslOneBangkok2024(metadata).build()

        print(f"Now optimising for {team.name}")

        # Optimise
        total_points = [
            ept_dl_s24_gs1.obtained_points[t_index] +
            ept_dl_s24_gs2.obtained_points[t_index] +
            ept_dl_s24.obtained_points[t_index] +
            ept_esl_one_bkk_2024_gs.obtained_points[t_index] +
            ept_esl_one_bkk.obtained_points[t_index]
            for t in teams
            if (t_index := team_database.get_team_index(t)) is not None
        ]

        cutoff = 8
        add_optimisation_constraints(model, team, team_database, teams, total_points, cutoff)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status != cp_model.OPTIMAL:
            print(f"Team {team.name} probably cannot finish in top 8")
            continue

        if solver.objective_value > max_objective_value:
            max_objective_value = solver.objective_value

            display: Display = Display([ept_dl_s24, ept_esl_one_bkk], metadata)
            display.print(team, cutoff, max_objective_value, solver)

            for t in teams:
                t_index = team_database.get_team_index(t)
                print(f"Team {t.name} points: {solver.value(total_points[t_index])}")
                print(
                    f"Team {t.name} DreamLeague Season 24 GS1 points: {solver.value(ept_dl_s24_gs1.obtained_points[t_index])}")
                print(
                    f"Team {t.name} DreamLeague Season 24 GS2 points: {solver.value(ept_dl_s24_gs2.obtained_points[t_index])}")
                print(
                    f"Team {t.name} DreamLeague Season 24 overall points: {solver.value(ept_dl_s24.obtained_points[t_index])}")
                print(
                    f"Team {t.name} ESL One Bangkok 2024 GS points: {solver.value(ept_esl_one_bkk_2024_gs.obtained_points[t_index])}")
                print(
                    f"Team {t.name} ESL One Bangkok 2024 overall points: {solver.value(ept_esl_one_bkk.obtained_points[t_index])}")

        print(f"Maximum objective value: {max_objective_value}")


def add_optimisation_constraints(model, team, team_database, teams, total_points, cutoff: int):
    team_count_range = range(len(teams))
    ranks: [IntVar] = {team: model.NewIntVar(1, len(teams), f'ranks_{team}') for team in team_count_range}
    aux: [[BooleanVar]] = {(i, j): model.NewBoolVar(f'aux_{i}_{j}') for i in team_count_range for j in
                           team_count_range}
    big_m: int = 10000
    for i in team_count_range:
        for j in team_count_range:
            if i == j:
                model.Add(aux[(i, j)] == 1)
            else:
                model.Add(total_points[i] - total_points[j] <= (1 - aux[(i, j)]) * big_m)
                model.Add(total_points[j] - total_points[i] <= aux[(i, j)] * big_m)
        ranks[i] = sum(aux[(i, j)] for j in team_count_range)
    team_index: int = team_database.get_team_index(team)
    model.Add(ranks[team_index] > cutoff)
    model.Maximize(total_points[team_index])


def print_single_match(teams: [Team], match: SingleMatch, solver: CpSolver, team_database: TeamDatabase):
    winner: Team | None = None
    loser: Team | None = None
    for team in teams:
        team_index: int = team_database.get_team_index(team)
        if solver.values(match.indicators[team_index]).iloc[0] == 1 and \
                solver.values(match.indicators[team_index]).iloc[1] == 0:
            winner = team
            continue

        if solver.values(match.indicators[team_index]).iloc[0] == 0 and \
                solver.values(match.indicators[team_index]).iloc[1] == 1:
            loser = team
            continue

    if winner is None or loser is None:
        winner_name = winner.name if winner is not None else "None"
        loser_name = loser.name if loser is not None else "None"
        print(f"{match.name} has no winner {winner_name} or loser {loser_name}")
    else:
        print(f"{match.name}: {winner.name} beat {loser.name}")


main()
