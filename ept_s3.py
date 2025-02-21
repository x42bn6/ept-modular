from ortools.constraint_solver.pywrapcp import BooleanVar
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, CpSolver, IntVar

from display import Display
from ept import EptTournament
from metadata import Metadata
from stage import SingleMatch
from teams import Team, Region, TeamDatabase
from tournaments.dreamleague_season_24 import DreamLeagueSeason24
from tournaments.dreamleague_season_25 import DreamLeagueSeason25
from tournaments.esl_one_bangkok_2024 import EslOneBangkok2024
from transfer_window import TransferWindow


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
        Team("9Pandas", Region.EEU),

        Team("Team Falcons", Region.MESWA),
        Team("Nigma Galaxy", Region.MESWA),
        Team("Chimera Esports", Region.MESWA),

        Team("Nouns Esports", Region.NA),
        Team("Atlantic City", Region.NA),
        Team("Shopify Rebellion", Region.NA),

        Team("HEROIC", Region.SA),
        Team("Team Waska", Region.SA),
        Team("beastcoast", Region.SA),

        Team("Xtreme Gaming", Region.CN),
        Team("Azure Ray", Region.CN),
        Team("Gaozu", Region.CN),
        Team("Yakult Brothers", Region.CN),

        Team("Talon Esports", Region.SEA),
        Team("BOOM Esports", Region.SEA),
        Team("Moodeng Warriors", Region.SEA),
    ]
    team_database: TeamDatabase = TeamDatabase()
    for team in teams:
        team_database.add_team(team)

    max_objective_value = -1
    for team in team_database.get_all_teams():
        model: CpModel = CpModel()
        metadata: [Metadata] = Metadata(team_database, model)

        ept_dl_s24, ept_dl_s24_gs1, ept_dl_s24_gs2 = DreamLeagueSeason24(metadata).build()

        dl_s24_to_esl_one_bkk_2024: TransferWindow = TransferWindow("dl_s24_to_esl_one_bkk_2024", team_database)
        dl_s24_to_esl_one_bkk_2024.add_change("Xtreme Gaming", -675)
        dl_s24_to_esl_one_bkk_2024.add_change("Nouns Esports", -30)
        dl_s24_to_esl_one_bkk_2024.add_change("Atlantic City", 30)
        dl_s24_to_esl_one_bkk_2024.add_change("Azure Ray", -125)

        ept_esl_one_bkk_2024, ept_esl_one_bkk_2024_gs = EslOneBangkok2024(metadata).build()

        esl_one_bkk_2024_to_dl_s25: TransferWindow = TransferWindow("esl_one_bkk_2024_to_dl_s25", team_database)
        esl_one_bkk_2024_to_dl_s25.add_change("Team Spirit", -1320)
        esl_one_bkk_2024_to_dl_s25.add_change("Tundra Esports", -382)
        esl_one_bkk_2024_to_dl_s25.add_change("HEROIC", -21)
        esl_one_bkk_2024_to_dl_s25.add_change("Gaozu", -126)
        esl_one_bkk_2024_to_dl_s25.add_change("Palianytsia", -9)
        esl_one_bkk_2024_to_dl_s25.add_change("Team Waska", -550)
        esl_one_bkk_2024_to_dl_s25.add_change("Atlantic City", -30)

        ept_dl_s25, ept_dl_s25_gs1, ept_dl_s25_gs2 = DreamLeagueSeason25(metadata).build()

        dl_s25_to_esl_one_ral_2025: TransferWindow = TransferWindow("dl_s25_to_esl_one_ral_2025", team_database)
        dl_s25_to_esl_one_ral_2025.add_change("Palianytsia", -21)

        print(f"Now optimising for {team.name}")

        # Optimise
        total_points = [
            ept_dl_s24_gs1.obtained_points[t_index] +
            ept_dl_s24_gs2.obtained_points[t_index] +
            ept_dl_s24.obtained_points[t_index] +
            dl_s24_to_esl_one_bkk_2024.get_change(t_index) +
            ept_esl_one_bkk_2024_gs.obtained_points[t_index] +
            ept_esl_one_bkk_2024.obtained_points[t_index] +
            esl_one_bkk_2024_to_dl_s25.get_change(t_index) +
            ept_dl_s25_gs1.obtained_points[t_index] +
            ept_dl_s25_gs2.obtained_points[t_index] +
            ept_dl_s25.obtained_points[t_index] +
            dl_s25_to_esl_one_ral_2025.get_change(t_index)
            for t in teams
            if (t_index := team_database.get_team_index(t)) is not None
        ]

        cutoff = 4
        add_optimisation_constraints(model, team, team_database, teams, total_points, cutoff)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status != cp_model.OPTIMAL:
            print(f"Team {team.name} probably cannot finish in top f{cutoff}")
            continue

        if solver.objective_value > max_objective_value:
            max_objective_value = solver.objective_value

            display: Display = Display([
                ept_dl_s24,
                dl_s24_to_esl_one_bkk_2024,
                ept_esl_one_bkk_2024,
                esl_one_bkk_2024_to_dl_s25,
                ept_dl_s25,
                dl_s25_to_esl_one_ral_2025
            ], metadata)
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
                    f"Team {t.name} ESL One Bangkok 2024 overall points: {solver.value(ept_esl_one_bkk_2024.obtained_points[t_index])}")
                print(
                    f"Team {t.name} DreamLeague Season 25 GS1 points: {solver.value(ept_dl_s25_gs1.obtained_points[t_index])}")
                print(
                    f"Team {t.name} DreamLeague Season 25 GS2 points: {solver.value(ept_dl_s25_gs2.obtained_points[t_index])}")
                print(
                    f"Team {t.name} DreamLeague Season 25 overall points: {solver.value(ept_dl_s25.obtained_points[t_index])}")

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
