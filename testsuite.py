from ortools.constraint_solver.pywrapcp import BooleanVar
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, IntVar

from ept import EptGroupStage, EptTournament
from metadata import Metadata
from stage import Root, GroupStage, Tournament
from teams import Team, TeamDatabase


def main():
    teams: [Team] = [
        Team("A"),
        Team("B"),
        Team("C"),
        Team("D")
    ]

    team_database: TeamDatabase = TeamDatabase()
    for team in teams:
        team_database.add_team(team)

    max_objective_value = -1
    max_solver = None
    max_team = None
    for team in team_database.get_all_teams():
        model: CpModel = CpModel()
        metadata = Metadata(team_database, model)

        root: Root = Root("root", len(teams), metadata, teams=teams)
        group_stage_1: GroupStage = GroupStage("group_stage_1", len(teams), 2, metadata)
        group_stage_2: GroupStage = GroupStage("group_stage_2", 2, 0, metadata)
        tournament: Tournament = Tournament("tournament", group_stage_1, metadata)
        root.bind_forward(group_stage_1)
        group_stage_1.bind_forward(group_stage_2)
        root.build()
        group_stage_1.build()
        group_stage_2.build()
        tournament.build()

        ept_group_stage_1: EptGroupStage = EptGroupStage(group_stage_1, [100, 50])
        ept_group_stage_1.build()
        ept_group_stage_2: EptGroupStage = EptGroupStage(group_stage_2, [100])
        ept_group_stage_2.build()
        ept_tournament: EptTournament = EptTournament(tournament, [1000, 500, 250, 100])
        ept_tournament.build()

        print(f"Now optimising for {team.name}")

        # Optimise
        total_points = [
            ept_group_stage_1.obtained_points[t_index] +
            ept_group_stage_2.obtained_points[t_index] +
            ept_tournament.obtained_points[t_index]
            for t in teams
            if (t_index := team_database.get_team_index(t)) is not None
        ]

        team_count_range = range(len(teams))
        ranks: [IntVar] = {team: model.NewIntVar(1, len(teams), f'ranks_{team}') for team in team_count_range}
        aux: [[BooleanVar]] = {(i, j): model.NewBoolVar(f'aux_{i}_{j}') for i in team_count_range for j in
                               team_count_range}
        big_m: int = 20000
        for i in team_count_range:
            for j in team_count_range:
                if i == j:
                    model.Add(aux[(i, j)] == 1)
                else:
                    model.Add(total_points[i] - total_points[j] <= (1 - aux[(i, j)]) * big_m)
                    model.Add(total_points[j] - total_points[i] <= aux[(i, j)] * big_m)
            ranks[i] = sum(aux[(i, j)] for j in team_count_range)

        team_index: int = team_database.get_team_index(team)
        model.Add(ranks[team_index] > 2)
        model.Maximize(total_points[team_index])

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status != cp_model.OPTIMAL:
            print(f"Team {team.name} probably cannot finish in top 2")
            continue

        if solver.objective_value > max_objective_value:
            max_objective_value = solver.objective_value

            for t in teams:
                t_index = team_database.get_team_index(t)
                print(f"Team {t.name} points: {solver.value(total_points[t_index])}")
                print(f"Team {t.name} GS1 points: {solver.value(ept_group_stage_1.obtained_points[t_index])}")
                print(f"Team {t.name} GS2 points: {solver.value(ept_group_stage_2.obtained_points[t_index])}")
                print(f"Team {t.name} Tournament points: {solver.value(ept_tournament.obtained_points[t_index])}")

            max_solver = solver
            max_team = team
            print(max_objective_value)


main()
