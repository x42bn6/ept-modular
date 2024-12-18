from ortools.constraint_solver.pywrapcp import BooleanVar
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, CpSolver, IntVar

from display import Display
from ept import EptGroupStage, EptPairGroupStage, EptTournament
from metadata import Metadata
from stage import GroupStage, PairGroupStage, Tournament, SingleMatch, DoubleElimination_2U2L1D
from teams import Team, Region, TeamDatabase
from utilities import print_indicators


def main():
    teams: [Team] = [
        Team("Team Liquid", Region.WEU),
        Team("Gaimin Gladiators", Region.WEU),
        Team("Team Falcons", Region.MESWA),
        Team("Xtreme Gaming", Region.CN),
        Team("BetBoom Team", Region.EEU),
        Team("Tundra Esports", Region.WEU),
        Team("AVULUS", Region.WEU),
        Team("Palianytsia", Region.WEU),
        Team("PARIVISION", Region.EEU),
        Team("Team Spirit", Region.EEU),
        Team("Nigma Galaxy", Region.MESWA),
        Team("Azure Ray", Region.CN),
        Team("Talon Esports", Region.SEA),
        Team("Nouns Esports", Region.NA),
        Team("HEROIC", Region.SA),
        Team("Team Waska", Region.SA)
    ]
    team_database: TeamDatabase = TeamDatabase()
    for team in teams:
        team_database.add_team(team)

    max_objective_value = -1
    for team in team_database.get_all_teams():
        model: CpModel = CpModel()
        metadata: [Metadata] = Metadata(team_database, model)

        dl_s24_gs1: PairGroupStage = PairGroupStage("dl_s24_gs1", 8, 4, metadata)
        dl_s24_gs2: GroupStage = GroupStage("dl_s24_gs2", 8, 4, metadata)
        dl_s24_playoff: DoubleElimination_2U2L1D = DoubleElimination_2U2L1D("dl_s24_playoff", metadata)
        dl_s24: Tournament = Tournament("dl_s24", dl_s24_gs1, metadata)

        dl_s24_gs1.group_a = team_database.get_teams_by_names("PARIVISION", "Team Liquid", "Xtreme Gaming",
                                                              "BetBoom Team", "Gaimin Gladiators",
                                                              "AVULUS", "Nigma Galaxy", "Nouns Esports")
        dl_s24_gs1.group_b = team_database.get_teams_by_names("Team Falcons", "Team Waska", "Tundra Esports",
                                                              "Team Spirit", "Talon Esports", "Azure Ray", "HEROIC",
                                                              "Palianytsia")

        dl_s24_gs1.bind_forward(dl_s24_gs2)
        dl_s24_playoff.bind_backward(dl_s24_gs2)
        dl_s24_gs2.bind_forward(dl_s24_playoff)


        ept_dl_s24_gs1 = EptPairGroupStage(dl_s24_gs1, [300, 150, 75])
        ept_dl_s24_gs2 = EptGroupStage(dl_s24_gs2, [300])
        ept_dl_s24_gs1.bind_next_ept_stage(ept_dl_s24_gs2)
        ept_dl_s24 = EptTournament(dl_s24,
                                   ept_dl_s24_gs1,
                                   [3000, 2500, 2000, 1600, 1200, 1000, 600, 400, 250, 250, 125, 125, 70, 70, 30, 30],
                                   metadata)

        dl_s24_gs1.team_can_finish_between("PARIVISION", 1, 2)
        dl_s24_gs1.team_can_finish_between("Team Liquid", 3, 4)
        dl_s24_gs1.team_can_finish_between("Xtreme Gaming", 5, 6)
        dl_s24_gs1.team_can_finish_between("BetBoom Team", 7, 8)
        dl_s24_gs1.team_can_finish_between("Gaimin Gladiators", 9, 10)
        dl_s24_gs1.team_can_finish_between("AVULUS", 11, 12)
        dl_s24_gs1.team_can_finish_between("Nigma Galaxy", 13, 14)
        dl_s24_gs1.team_can_finish_between("Nouns Esports", 15, 16)

        dl_s24_gs1.team_can_finish_between("Team Falcons", 1, 2)
        dl_s24_gs1.team_can_finish_between("Team Waska", 3, 4)
        dl_s24_gs1.team_can_finish_between("Tundra Esports", 5, 6)
        dl_s24_gs1.team_can_finish_between("Team Spirit", 7, 8)
        dl_s24_gs1.team_can_finish_between("Talon Esports", 9, 10)
        dl_s24_gs1.team_can_finish_between("Azure Ray", 11, 12)
        dl_s24_gs1.team_can_finish_between("HEROIC", 13, 14)
        dl_s24_gs1.team_can_finish_between("Palianytsia", 15, 16)

        dl_s24_gs2.team_can_finish_between("BetBoom Team", 1, 1)
        dl_s24_gs2.team_can_finish_between("Team Spirit", 2, 2)
        dl_s24_gs2.team_can_finish_between("PARIVISION", 3, 3)
        dl_s24_gs2.team_can_finish_between("Team Falcons", 4, 4)
        dl_s24_gs2.team_can_finish_between("Tundra Esports", 5, 5)
        dl_s24_gs2.team_can_finish_between("Team Liquid", 6, 6)
        dl_s24_gs2.team_can_finish_between("Xtreme Gaming", 7, 7)
        dl_s24_gs2.team_can_finish_between("Team Waska", 8, 8)

        dl_s24_playoff.ubf.set_winner("BetBoom Team")
        dl_s24_playoff.lbsf.set_winner("Team Falcons")
        dl_s24_playoff.lbf.set_winner("Team Falcons")
        dl_s24_playoff.gf.set_winner("Team Falcons")

        dl_s24_gs1.build()
        dl_s24_gs2.build()
        dl_s24_playoff.build()
        dl_s24.build()

        ept_dl_s24_gs1.build()
        ept_dl_s24_gs2.build()
        ept_dl_s24.build()

        print(f"Now optimising for {team.name}")

        # Optimise
        total_points = [
            ept_dl_s24_gs1.obtained_points[t_index] +
            ept_dl_s24_gs2.obtained_points[t_index] +
            ept_dl_s24.obtained_points[t_index]
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

            display: Display = Display([ept_dl_s24], metadata)
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
