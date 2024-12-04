from ortools.constraint_solver.pywrapcp import BooleanVar
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, IntVar, CpSolver

from ept import EptGroupStage, EptTournament, EptPairGroupStage
from metadata import Metadata
from stage import Root, GroupStage, Tournament, PairGroupStage, SingleMatch
from teams import Team, TeamDatabase


def main():
    # basic_two_group_stage()
    # pair_group_stage_into_single_group_stage()
    # single_match()
    bracket_4u2l1d()


def basic_two_group_stage():
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

        add_optimisation_constraints(model, team, team_database, teams, total_points, 1)

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
            print(max_objective_value)


def pair_group_stage_into_single_group_stage():
    teams: [Team] = [
        Team("A"),
        Team("B"),
        Team("C"),
        Team("D"),
        Team("E"),
        Team("F"),
        Team("G"),
        Team("H")
    ]
    team_database: TeamDatabase = TeamDatabase()
    for team in teams:
        team_database.add_team(team)

    max_objective_value = -1
    for team in team_database.get_all_teams():
        model: CpModel = CpModel()
        metadata = Metadata(team_database, model)

        root: Root = Root("root", len(teams), metadata, teams=teams)
        group_stage_1: PairGroupStage = PairGroupStage("group_stage_1",
                                                       4,
                                                       2,
                                                       metadata,
                                                       group_a=team_database.get_teams_by_names("A", "B", "C", "D"),
                                                       group_b=team_database.get_teams_by_names("E", "F", "G", "H")
                                                       )
        group_stage_2: GroupStage = GroupStage("group_stage_2", 4, 0, metadata)
        tournament: Tournament = Tournament("tournament", group_stage_1, metadata)

        root.bind_forward(group_stage_1)
        group_stage_1.bind_forward(group_stage_2)

        root.build()
        group_stage_1.build()
        group_stage_2.build()
        tournament.build()

        ept_group_stage_1: EptPairGroupStage = EptPairGroupStage(group_stage_1, [300, 100, 50])
        ept_group_stage_1.build()
        ept_group_stage_2: EptGroupStage = EptGroupStage(group_stage_2, [300])
        ept_group_stage_2.build()
        ept_tournament: EptTournament = EptTournament(tournament, [1000, 500, 250, 100, 50, 25, 10, 5])
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

        add_optimisation_constraints(model, team, team_database, teams, total_points, 4)

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
            print(max_objective_value)


def single_match():
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
    for team in team_database.get_all_teams():
        model: CpModel = CpModel()
        metadata = Metadata(team_database, model)

        ub1: SingleMatch = SingleMatch("ub1", metadata, team_database.get_teams_by_names("A", "B"))
        ub2: SingleMatch = SingleMatch("ub2", metadata, team_database.get_teams_by_names("C", "D"))
        gf: SingleMatch = SingleMatch("gf", metadata)
        ub1.bind_winner(gf)
        ub2.bind_winner(gf)

        ub1.build()
        ub2.build()
        gf.build()

        print(f"Now optimising for {team.name}")

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status != cp_model.OPTIMAL:
            print(f"Team {team.name} probably cannot finish in top 1")
            continue

        if solver.objective_value > max_objective_value:
            max_objective_value = solver.objective_value
            for t in teams:
                t_index = team_database.get_team_index(t)
                print(f"{t.name} => {solver.values(ub1.indicators[t_index])}")
                print(f"{t.name} => {solver.values(ub2.indicators[t_index])}")
                print(f"{t.name} => {solver.values(gf.indicators[t_index])}")
            print(max_objective_value)


def print_single_match(teams: [Team], match: SingleMatch, solver: CpSolver, team_database: TeamDatabase):
    winner: Team = None
    loser: Team = None
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
        print(f"{match.name} has no winner {winner} or loser {loser}")
    else:
        print(f"{match.name}: {winner.name} beat {loser.name}")


def bracket_4u2l1d():
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
    for team in team_database.get_all_teams():
        model: CpModel = CpModel()
        metadata = Metadata(team_database, model)

        ubr1_1: SingleMatch = SingleMatch("ubr1_1", metadata, team_database.get_teams_by_names("A", "B"))
        ubr1_2: SingleMatch = SingleMatch("ubr1_2", metadata, team_database.get_teams_by_names("C", "D"))
        ubf: SingleMatch = SingleMatch("ubf", metadata)
        lbsf: SingleMatch = SingleMatch("lbsf", metadata)
        lbf: SingleMatch = SingleMatch("lbf", metadata)
        gf: SingleMatch = SingleMatch("gf", metadata)

        group_stage: GroupStage = GroupStage("group_stage", 1, 0, metadata)
        tournament: Tournament = Tournament("tournament", group_stage, metadata)

        ubr1_1.bind_winner(ubf)
        ubr1_1.bind_loser(lbsf)
        ubr1_2.bind_winner(ubf)
        ubr1_2.bind_loser(lbsf)
        ubf.bind_winner(gf)
        ubf.bind_loser(lbf)
        lbsf.bind_winner(lbf)
        lbf.bind_winner(gf)
        gf.bind_qualification(group_stage)

        ubr1_1.build()
        ubr1_2.build()
        ubf.build()
        lbsf.build()
        lbf.build()
        gf.build()
        group_stage.build()
        tournament.build()

        ept_group_stage: EptGroupStage = EptGroupStage(group_stage, [100])
        ept_group_stage.build()
        ept_tournament: EptTournament = EptTournament(tournament, [1000])
        ept_tournament.build()

        print(f"Now optimising for {team.name}")

        # Optimise
        total_points = [
            ept_group_stage.obtained_points[t_index] +
            ept_tournament.obtained_points[t_index]
            for t in teams
            if (t_index := team_database.get_team_index(t)) is not None
        ]

        add_optimisation_constraints(model, team, team_database, teams, total_points, 1)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status != cp_model.OPTIMAL:
            print(f"Team {team.name} probably cannot finish in top 1")
            continue

        if solver.objective_value > max_objective_value:
            max_objective_value = solver.objective_value
            print_single_match(teams, ubr1_1, solver, team_database)
            print_single_match(teams, ubr1_2, solver, team_database)
            print_single_match(teams, ubf, solver, team_database)
            print_single_match(teams, lbsf, solver, team_database)
            print_single_match(teams, lbf, solver, team_database)
            print_single_match(teams, gf, solver, team_database)

            for t in teams:
                t_index = team_database.get_team_index(t)
                print(f"Team {t.name} points: {solver.value(total_points[t_index])}")
                print(f"Team {t.name} GS1 points: {solver.value(ept_group_stage.obtained_points[t_index])}")
                print(f"Team {t.name} Tournament points: {solver.value(ept_tournament.obtained_points[t_index])}")
            print(max_objective_value)


def add_optimisation_constraints(model, team, team_database, teams, total_points, cutoff: int):
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
    model.Add(ranks[team_index] > cutoff)
    model.Maximize(total_points[team_index])


main()
