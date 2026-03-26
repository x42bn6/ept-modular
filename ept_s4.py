import sys
import time
from typing import TextIO

from ortools.constraint_solver.pywrapcp import BooleanVar
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, CpSolver, IntVar

from constants import BIG_M
from display import Display
from display_phases import HasDisplayPhase
from ept import EptTournamentBase
from metadata import Metadata
from stage import SingleMatch
from teams import Team, Region, TeamDatabase
from tournaments.dreamleague_season_27 import DreamLeagueSeason27Solved
from tournaments.dreamleague_season_28 import DreamLeagueSeason28Solved
from tournaments.dreamleague_season_29 import DreamLeagueSeason29
from tournaments.esl_one_birmingham_2026 import EslOneBirmingham2026
from transfer_window import TransferWindow


def main():

    teams: [Team] = [
        Team("Tundra Esports", Region.WEU),
        Team("Team Liquid", Region.WEU),
        Team("Team Falcons", Region.WEU),
        Team("MOUZ", Region.WEU),
        Team("Virtus.pro", Region.WEU),
        Team("Natus Vincere", Region.WEU),
        Team("Nigma Galaxy", Region.WEU),
        Team("Pipsqueak+4", Region.WEU),
        Team("Passion UA", Region.WEU),
        Team("Pasika UA", Region.WEU),
        Team("WEU Team 1", Region.WEU, is_pseudo_team=True),
        Team("WEU Team 2", Region.WEU, is_pseudo_team=True),
        Team("WEU Team 3", Region.WEU, is_pseudo_team=True),
        Team("WEU Team 4", Region.WEU, is_pseudo_team=True),

        Team("Aurora Gaming", Region.EEU),
        Team("Team Yandex", Region.EEU),
        Team("Team Spirit", Region.EEU),
        Team("PARIVISION", Region.EEU),
        Team("BetBoom Team", Region.EEU),
        Team("Power Rangers (stack)", Region.EEU),
        Team("1w Team", Region.EEU),
        Team("Runa Team", Region.EEU),
        Team("EEU Team 1", Region.EEU, is_pseudo_team=True),
        Team("EEU Team 2", Region.EEU, is_pseudo_team=True),
        Team("EEU Team 3", Region.EEU, is_pseudo_team=True),
        Team("EEU Team 4", Region.EEU, is_pseudo_team=True),

        Team("GamerLegion", Region.NA),
        Team("NA Team 1", Region.NA, is_pseudo_team=True),

        Team("HEROIC", Region.SA),
        Team("paiN Gaming", Region.SA),
        Team("Amaru Gaming", Region.SA),
        Team("SA Team 1", Region.SA, is_pseudo_team=True),
        Team("SA Team 2", Region.SA, is_pseudo_team=True),

        Team("Xtreme Gaming", Region.CN),
        Team("Yakult Brothers", Region.CN),
        Team("Vici Gaming", Region.CN),
        Team("Team Tidebound", Region.CN),
        Team("CN Team 1", Region.CN, is_pseudo_team=True),
        Team("CN Team 2", Region.CN, is_pseudo_team=True),

        Team("OG", Region.SEA),
        Team("REKONIX", Region.SEA),
        Team("Execration", Region.SEA),
        Team("Team Nemesis", Region.SEA),
        Team("SEA Team 1", Region.SEA, is_pseudo_team=True),
        Team("SEA Team 2", Region.SEA, is_pseudo_team=True),
    ]
    team_database: TeamDatabase = TeamDatabase()
    for team in teams:
        team_database.add_team(team)

    def spirit_top_12(m: CpModel, r: [IntVar]):
        m.Add(r[team_database.get_team_index_by_team_name("Team Spirit")] <= 12)

    spirit_top_12_file = open("spirit-top-12.txt", "w")
    optimise_and_write(13, "Top 13", spirit_top_12_file, team_database, [spirit_top_12])

    def spirit_not_top_12(m: CpModel, r: [IntVar]):
        m.Add(r[team_database.get_team_index_by_team_name("Team Spirit")] > 12)

    spirit_not_top_12_file = open("spirit-not-top-12.txt", "w")
    #optimise_and_write(12, "Top 12", spirit_not_top_12_file, team_database, [spirit_not_top_12])


def optimise_and_write(cutoff: int, header: str, file: TextIO, team_database: TeamDatabase, scenarios=None):
    if scenarios is None:
        scenarios = [lambda m, r: None]
    teams: [Team] = team_database.get_all_teams()
    start_time = get_epoch_time_seconds()
    min_cutoff_teams: [Team] = []
    max_objective_value_teams: [Team] = []
    min_cutoff = sys.maxsize
    max_cutoff_plus_one = -1
    max_cutoff_plus_one, max_objective_value_teams = optimise_maximise_cutoff_plus_one(cutoff,
                                                                                       max_cutoff_plus_one,
                                                                                       max_objective_value_teams,
                                                                                       team_database,
                                                                                       team_database.get_all_teams(),
                                                                                       scenarios)

    print(
        f"Found maximum cutoff plus one value as {max_cutoff_plus_one} for teams {[team.name for team in max_objective_value_teams]}.  Now minimising cutoff")
    # Track pseudo-teams.  All of them are basically the same, so optimising for one is the same as the others.  Skip if done
    regions_with_pseudo_teams_solved: [Region] = []
    for team in team_database.get_all_teams():
        if team.is_pseudo_team:
            if team.region in regions_with_pseudo_teams_solved:
                continue
            else:
                regions_with_pseudo_teams_solved.append(team.region)

        for max_objective_value_team in max_objective_value_teams:
            if team == max_objective_value_team:
                continue

            model: CpModel = CpModel()
            metadata: [Metadata] = Metadata(team_database, model)
            full_ept = FullEpt(metadata)
            phases: [HasDisplayPhase] = full_ept.get_display_phases()

            print(f"Now optimising for {team.name}")
            max_possible_points_for_team = calculate_theoretical_maximum_for_team(phases, team, team_database)
            if max_cutoff_plus_one > max_possible_points_for_team:
                print(
                    f"Team {team.name}'s maximum points ({max_possible_points_for_team}) is less than objective value ({max_cutoff_plus_one}).  Skipping")
                continue

            # Optimise
            total_points = full_ept.get_total_points(team_database, teams)
            minimise_cutoff(model, team, team_database, teams, total_points, cutoff, max_objective_value_team,
                            max_cutoff_plus_one, scenarios)

            solver = cp_model.CpSolver()
            status = solver.Solve(model)
            if status != cp_model.OPTIMAL:
                print(f"Team {team.name} probably cannot finish in position {cutoff}")
                continue

            # I really don't like doing this, but there is a stupid scenario where one is something like 999.999 and one is 1000.0001
            new_objective_value = round(solver.objective_value)
            if new_objective_value < min_cutoff:
                min_cutoff = solver.objective_value
                min_cutoff_teams = [team]
            elif new_objective_value == min_cutoff:
                min_cutoff_teams.append(team)
            else:
                print(
                    f"Minimum objective value for {team.name} ({solver.objective_value}) is not less than current minimum {min_cutoff}")
                continue

            display: Display = Display(phases, metadata)
            file.write(display.print(header, team, cutoff, min_cutoff, solver))
            print(f"Objective value: {min_cutoff}")
    print(
        f"Got cutoff value as {min_cutoff} for team {[team.name for team in min_cutoff_teams]} with corresponding teams {[team.name for team in max_objective_value_teams]} missing out with {max_cutoff_plus_one}")
    end_time = get_epoch_time_seconds()
    print(f"Completed in {end_time - start_time}s")


def get_epoch_time_seconds():
    return round(time.time())


def optimise_maximise_cutoff_plus_one(cutoff, max_cutoff_plus_one, max_objective_value_teams, team_database, teams,
                                      scenarios):
    # Track pseudo-teams.  All of them are basically the same, so optimising for one is the same as the others.  Skip if done
    regions_with_pseudo_teams_solved: [Region] = []
    for team in team_database.get_all_teams():
        if team.is_pseudo_team:
            if team.region in regions_with_pseudo_teams_solved:
                continue
            else:
                regions_with_pseudo_teams_solved.append(team.region)

        model: CpModel = CpModel()
        metadata: [Metadata] = Metadata(team_database, model)

        full_ept = FullEpt(metadata)
        phases: [HasDisplayPhase] = full_ept.get_display_phases()

        print(f"Now optimising for {team.name}")
        max_possible_points_for_team = calculate_theoretical_maximum_for_team(phases, team, team_database)
        if max_cutoff_plus_one > max_possible_points_for_team:
            print(
                f"Team {team.name}'s maximum points ({max_possible_points_for_team}) is less than objective value ({max_cutoff_plus_one}).  Skipping")
            continue

        # Optimise
        total_points = full_ept.get_total_points(team_database, teams)
        maximise_cutoff_plus_one(model, team, team_database, teams, total_points, cutoff, scenarios)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if status != cp_model.OPTIMAL:
            print(f"Team {team.name} probably cannot finish in position {cutoff}")
            continue

        # I really don't like doing this, but there is a stupid scenario where one is something like 999.999 and one is 1000.0001
        new_objective_value = round(solver.objective_value)
        if new_objective_value > max_cutoff_plus_one:
            max_objective_value_teams = [team]
            max_cutoff_plus_one = new_objective_value
        elif new_objective_value == max_cutoff_plus_one:
            max_objective_value_teams.append(team)
        else:
            print(
                f"Maximum objective value for {team.name} ({solver.objective_value}) is not greater than current maximum {max_cutoff_plus_one}")
            continue

        print(f"Maximum objective value: {max_cutoff_plus_one}")

    return max_cutoff_plus_one, max_objective_value_teams


def calculate_theoretical_maximum_for_team(phases, team, team_database):
    # Calculate theoretical maximum.  If this is less than the current maximum, don't bother solving
    max_possible_points_for_team: int = 0
    for phase in phases:
        if isinstance(phase, EptTournamentBase):
            max_possible_points_for_team += phase.get_maximum_points_for_team(team)
        elif isinstance(phase, TransferWindow):
            max_possible_points_for_team += phase.get_change(team_database.get_team_index(team))
    return max_possible_points_for_team


def maximise_cutoff_plus_one(model, team, team_database, teams, total_points, cutoff: int, scenarios):
    team_count_range = range(len(teams))
    ranks: [IntVar] = {team: model.NewIntVar(1, len(teams), f'ranks_{team}') for team in team_count_range}
    aux: [[BooleanVar]] = {(i, j): model.NewBoolVar(f'aux_{i}_{j}') for i in team_count_range for j in
                           team_count_range}
    for i in team_count_range:
        for j in team_count_range:
            if i == j:
                model.Add(aux[(i, j)] == 1)
            else:
                model.Add(total_points[i] - total_points[j] <= (1 - aux[(i, j)]) * BIG_M)
                model.Add(total_points[j] - total_points[i] <= aux[(i, j)] * BIG_M)
        ranks[i] = sum(aux[(i, j)] for j in team_count_range)
    team_index: int = team_database.get_team_index(team)
    model.Add(ranks[team_index] > cutoff)

    for scenario in scenarios:
        scenario(model, ranks)

    model.Maximize(total_points[team_index])


def minimise_cutoff(model, team, team_database, teams, total_points, cutoff: int, cutoff_team: Team,
                    cutoff_points: int, scenarios):
    team_count_range = range(len(teams))
    ranks: [IntVar] = {team: model.NewIntVar(1, len(teams), f'ranks_{team}') for team in team_count_range}
    aux: [[BooleanVar]] = {(i, j): model.NewBoolVar(f'aux_{i}_{j}') for i in team_count_range for j in
                           team_count_range}
    for i in team_count_range:
        for j in team_count_range:
            if i == j:
                model.Add(aux[(i, j)] == 1)
            else:
                model.Add(total_points[i] - total_points[j] <= (1 - aux[(i, j)]) * BIG_M)
                model.Add(total_points[j] - total_points[i] <= aux[(i, j)] * BIG_M)
        ranks[i] = sum(aux[(i, j)] for j in team_count_range)
    team_index: int = team_database.get_team_index(team)
    cutoff_team_index: int = team_database.get_team_index(cutoff_team)
    model.Add(total_points[cutoff_team_index] == cutoff_points)
    model.Add(ranks[cutoff_team_index] == cutoff + 1)
    model.Add(ranks[team_index] == cutoff)

    for scenario in scenarios:
        scenario(model, ranks)

    model.Minimize(total_points[team_index])


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


class FullEpt:
    def __init__(self, metadata: Metadata):
        team_database: TeamDatabase = metadata.team_database

        ept_dl_s27 = DreamLeagueSeason27Solved(metadata).build()

        dl_s27_to_dl_s28: TransferWindow = TransferWindow("dl_s27_to_dl_s28", team_database)
        dl_s27_to_dl_s28.add_change("Aurora Gaming", -90)
        dl_s27_to_dl_s28.add_change("Power Rangers (stack)", 400)
        dl_s27_to_dl_s28.add_change("Yakult Brothers", -60)
        dl_s27_to_dl_s28.add_change("Vici Gaming", 280)
        dl_s27_to_dl_s28.add_change("Pasika UA", 200)
        dl_s27_to_dl_s28.add_change("Amaru Gaming", 300)
        dl_s27_to_dl_s28.add_change("1w Team", 200)
        dl_s27_to_dl_s28.add_change("Team Nemesis", -300)
        dl_s27_to_dl_s28.add_change("Passion UA", -200)
        dl_s27_to_dl_s28.add_change("Runa Team", -400)
        dl_s27_to_dl_s28.add_change("Team Tidebound", -400)

        ept_dl_s28, ept_dl_s28_gs1, ept_dl_s28_gs2 = DreamLeagueSeason28Solved(metadata).build()

        dl_s28_to_esl_one_bir_2026: TransferWindow = TransferWindow("dl_s28_to_esl_one_bir_2026", team_database)
        dl_s28_to_esl_one_bir_2026.add_change("Amaru Gaming", -90)

        ept_esl_one_bir_2026, ept_esl_one_bir_2026_gs = EslOneBirmingham2026(metadata).build()

        esl_one_bir_2026_to_dl_s29: TransferWindow = TransferWindow("esl_one_bir_2026_to_dl_s29", team_database)
        esl_one_bir_2026_to_dl_s29.add_change("Amaru Gaming", -63)
        esl_one_bir_2026_to_dl_s29.add_change("1w Team", -60)

        ept_dl_s29, ept_dl_s29_gs1, ept_dl_s29_gs2 = DreamLeagueSeason29(metadata).build()

        self.ept_dl_s27 = ept_dl_s27

        self.dl_s27_to_dl_s28 = dl_s27_to_dl_s28

        self.ept_dl_s28 = ept_dl_s28
        self.ept_dl_s28_gs1 = ept_dl_s28_gs1
        self.ept_dl_s28_gs2 = ept_dl_s28_gs2

        self.dl_s28_to_esl_one_bir_2026 = dl_s28_to_esl_one_bir_2026

        self.ept_esl_one_bir_2026 = ept_esl_one_bir_2026
        self.ept_esl_one_bir_2026_gs = ept_esl_one_bir_2026_gs

        self.esl_one_bir_2026_to_dl_s29 = esl_one_bir_2026_to_dl_s29

        self.ept_dl_s29 = ept_dl_s29
        self.ept_dl_s29_gs1 = ept_dl_s29_gs1
        self.ept_dl_s29_gs2 = ept_dl_s29_gs2

    def get_display_phases(self) -> [HasDisplayPhase]:
        return [
            self.ept_dl_s27,
            self.dl_s27_to_dl_s28,
            self.ept_dl_s28,
            self.dl_s28_to_esl_one_bir_2026,
            self.ept_esl_one_bir_2026,
            self.esl_one_bir_2026_to_dl_s29,
            self.ept_dl_s29,
        ]

    def get_total_points(self, team_database: TeamDatabase, teams: [Team]):
        return [
            self.ept_dl_s27.get_obtained_points(t_index) +
            self.dl_s27_to_dl_s28.get_change(t_index) +
            self.ept_dl_s28_gs1.get_obtained_points(t_index) +
            self.ept_dl_s28_gs2.get_obtained_points(t_index) +
            self.ept_dl_s28.get_obtained_points(t_index) +
            self.dl_s28_to_esl_one_bir_2026.get_change(t_index) +
            self.ept_esl_one_bir_2026_gs.get_obtained_points(t_index) +
            self.ept_esl_one_bir_2026.get_obtained_points(t_index) +
            self.esl_one_bir_2026_to_dl_s29.get_change(t_index) +
            self.ept_dl_s29_gs1.get_obtained_points(t_index) +
            self.ept_dl_s29_gs2.get_obtained_points(t_index) +
            self.ept_dl_s29.get_obtained_points(t_index)
            for t in teams
            if (t_index := team_database.get_team_index(t)) is not None
        ]


main()
