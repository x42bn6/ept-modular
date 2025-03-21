import sys
import time
from typing import Dict, TextIO

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
from tournaments.dreamleague_season_24 import DreamLeagueSeason24Solved
from tournaments.dreamleague_season_25 import DreamLeagueSeason25Solved
from tournaments.dreamleague_season_26 import DreamLeagueSeason26
from tournaments.esl_one_bangkok_2024 import EslOneBangkok2024Solved
from tournaments.esl_one_raleigh_2025 import EslOneRaleigh2025
from transfer_window import TransferWindow


def main():

    teams: [Team] = [
        Team("Team Liquid", Region.WEU),
        Team("Gaimin Gladiators", Region.WEU),
        Team("Tundra Esports", Region.WEU),
        Team("AVULUS", Region.WEU),
        Team("Palianytsia", Region.WEU, is_alive=False),

        Team("BetBoom Team", Region.EEU),
        Team("PARIVISION", Region.EEU),
        Team("Team Spirit", Region.EEU),
        Team("Natus Vincere", Region.EEU),
        Team("ex-9Pandas", Region.EEU),
        Team("9Pandas", Region.EEU, is_alive=False),

        Team("Team Falcons", Region.MESWA),
        Team("Nigma Galaxy", Region.MESWA),
        Team("Chimera Esports", Region.MESWA),

        Team("Nouns Esports", Region.NA, is_alive=False),
        Team("Atlantic City", Region.NA, is_alive=False),
        Team("Shopify Rebellion", Region.NA),

        Team("HEROIC", Region.SA),
        Team("Team Waska", Region.SA, is_alive=False),
        Team("beastcoast", Region.SA),

        Team("Xtreme Gaming", Region.CN),
        Team("ex-Xtreme Gaming", Region.CN),
        Team("Azure Ray", Region.CN, is_alive=False),
        Team("Gaozu", Region.CN, is_alive=False),
        Team("Yakult Brothers", Region.CN),
        Team("Team Tidebound", Region.CN),

        Team("Talon Esports", Region.SEA),
        Team("BOOM Esports", Region.SEA),
        Team("Moodeng Warriors", Region.SEA),
    ]
    teams_per_region: Dict[Region, int] = {
        Region.WEU: 3,
        Region.SA: 2,
        Region.SEA: 2,
        Region.NA: 1,
        Region.MESWA: 1,
        Region.CN: 2,
        Region.EEU: 1
    }
    for region in Region:
        for i in range(0, teams_per_region.get(region)):
            teams.append(Team(f"{region.name} team {i + 1}", region, is_pseudo_team=True))

    team_database: TeamDatabase = TeamDatabase()
    for team in teams:
        team_database.add_team(team)

    top_8_file = open("top-8.txt", "w")
    top_9_cn_file = open("top-9-cn.txt", "w")
    top_9_gg_file = open("top-9-gg.txt", "w")
    top_10_file = open("top-10.txt", "w")

    optimise_and_write(8, "Top 8", top_8_file, team_database)

    def gaimin_gladiators_top_8(m: CpModel, r: [IntVar]):
        m.Add(r[team_database.get_team_index_by_team_name("Gaimin Gladiators")] < 8)

    def gaimin_gladiators_not_top_8(m: CpModel, r: [IntVar]):
        m.Add(r[team_database.get_team_index_by_team_name("Gaimin Gladiators")] >= 8)

    def at_least_one_chinese_team_top_8(m: CpModel, r: [IntVar]):
        team_qualified: [BooleanVar] = []
        for t in team_database.get_teams_by_region(Region.CN):
            team_top_8 = m.new_bool_var(f"{t.name}_acl_top_8")
            team_index = team_database.get_team_index(t)
            m.Add(r[team_index] < 8).only_enforce_if(team_top_8)
            m.Add(r[team_index] >= 8).only_enforce_if(team_top_8.Not())
            team_qualified.append(team_top_8)
        m.AddBoolOr(team_qualified)

    def no_chinese_team_top_8(m: CpModel, r: [IntVar]):
        team_qualified: [BooleanVar] = []
        for t in team_database.get_teams_by_region(Region.CN):
            team_top_8 = m.new_bool_var(f"{t.name}_acl_top_8")
            team_index = team_database.get_team_index(t)
            m.Add(r[team_index] < 8).only_enforce_if(team_top_8)
            m.Add(r[team_index] >= 8).only_enforce_if(team_top_8.Not())
            team_qualified.append(team_top_8.Not())
        m.AddBoolAnd(team_qualified)

    optimise_and_write(9, "Top 9 (Chinese team guaranteed)", top_9_cn_file, team_database,
                       [at_least_one_chinese_team_top_8, gaimin_gladiators_not_top_8])
    optimise_and_write(9, "Top 9 (Gaimin Gladiators guaranteed)", top_9_gg_file, team_database,
                       [no_chinese_team_top_8, gaimin_gladiators_top_8])
    optimise_and_write(10, "Top 10", top_10_file, team_database,
                       [gaimin_gladiators_top_8, at_least_one_chinese_team_top_8])

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
        if not team.is_alive:
            continue

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


def optimise_maximise_cutoff_plus_one(cutoff, max_cutoff_plus_one, max_objective_value_teams, team_database, teams, scenarios):
    # Track pseudo-teams.  All of them are basically the same, so optimising for one is the same as the others.  Skip if done
    regions_with_pseudo_teams_solved: [Region] = []
    for team in team_database.get_all_teams():
        if not team.is_alive:
            continue

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

        ept_dl_s24, ept_dl_s24_gs1, ept_dl_s24_gs2 = DreamLeagueSeason24Solved(metadata).build()

        dl_s24_to_esl_one_bkk_2024: TransferWindow = TransferWindow("dl_s24_to_esl_one_bkk_2024", team_database)
        dl_s24_to_esl_one_bkk_2024.add_change("Xtreme Gaming", -675)
        dl_s24_to_esl_one_bkk_2024.add_change("Nouns Esports", -30)
        dl_s24_to_esl_one_bkk_2024.add_change("Atlantic City", 30)
        dl_s24_to_esl_one_bkk_2024.add_change("Azure Ray", -125)

        ept_esl_one_bkk_2024, ept_esl_one_bkk_2024_gs = EslOneBangkok2024Solved(metadata).build()

        esl_one_bkk_2024_to_dl_s25: TransferWindow = TransferWindow("esl_one_bkk_2024_to_dl_s25", team_database)
        esl_one_bkk_2024_to_dl_s25.add_change("Team Spirit", -1320)
        esl_one_bkk_2024_to_dl_s25.add_change("Tundra Esports", -382)
        esl_one_bkk_2024_to_dl_s25.add_change("HEROIC", -21)
        esl_one_bkk_2024_to_dl_s25.add_change("Gaozu", -126)
        esl_one_bkk_2024_to_dl_s25.add_change("Palianytsia", -9)
        esl_one_bkk_2024_to_dl_s25.add_change("Team Waska", -550)
        esl_one_bkk_2024_to_dl_s25.add_change("Atlantic City", -30)

        ept_dl_s25, ept_dl_s25_gs1, ept_dl_s25_gs2 = DreamLeagueSeason25Solved(metadata).build()

        dl_s25_to_esl_one_ral_2025: TransferWindow = TransferWindow("dl_s25_to_esl_one_ral_2025", team_database)
        dl_s25_to_esl_one_ral_2025.add_change("Palianytsia", -21)

        ept_esl_one_ral_2025, ept_esl_one_ral_2025_gs = EslOneRaleigh2025(metadata).build()

        esl_one_ral_2025_to_dl_s26: TransferWindow = TransferWindow("esl_one_ral_2025_to_dl_s26", team_database)
        esl_one_ral_2025_to_dl_s26.add_change("Xtreme Gaming", -98)
        esl_one_ral_2025_to_dl_s26.add_change("ex-Xtreme Gaming", 98)
        esl_one_ral_2025_to_dl_s26.add_change("9Pandas", -42)
        esl_one_ral_2025_to_dl_s26.add_change("ex-9Pandas", 42)
        esl_one_ral_2025_to_dl_s26.add_change("Gaozu", -294)
        esl_one_ral_2025_to_dl_s26.add_change("BOOM Esports", -155)

        ept_dl_s26, ept_dl_s26_gs1, ept_dl_s26_gs2 = DreamLeagueSeason26(metadata).build()

        self.ept_dl_s24 = ept_dl_s24
        self.ept_dl_s24_gs1 = ept_dl_s24_gs1
        self.ept_dl_s24_gs2 = ept_dl_s24_gs2

        self.dl_s24_to_esl_one_bkk_2024 = dl_s24_to_esl_one_bkk_2024

        self.ept_esl_one_bkk_2024 = ept_esl_one_bkk_2024
        self.ept_esl_one_bkk_2024_gs = ept_esl_one_bkk_2024_gs

        self.esl_one_bkk_2024_to_dl_s25 = esl_one_bkk_2024_to_dl_s25

        self.ept_dl_s25 = ept_dl_s25
        self.ept_dl_s25_gs1 = ept_dl_s25_gs1
        self.ept_dl_s25_gs2 = ept_dl_s25_gs2

        self.dl_s25_to_esl_one_ral_2025 = dl_s25_to_esl_one_ral_2025

        self.ept_esl_one_ral_2025 = ept_esl_one_ral_2025
        self.ept_esl_one_ral_2025_gs = ept_esl_one_ral_2025_gs

        self.esl_one_ral_2025_to_dl_s26 = esl_one_ral_2025_to_dl_s26

        self.ept_dl_s26 = ept_dl_s26
        self.ept_dl_s26_gs1 = ept_dl_s26_gs1
        self.ept_dl_s26_gs2 = ept_dl_s26_gs2

    def get_display_phases(self) -> [HasDisplayPhase]:
        return [
            self.ept_dl_s24,
            self.dl_s24_to_esl_one_bkk_2024,
            self.ept_esl_one_bkk_2024,
            self.esl_one_bkk_2024_to_dl_s25,
            self.ept_dl_s25,
            self.dl_s25_to_esl_one_ral_2025,
            self.ept_esl_one_ral_2025,
            self.esl_one_ral_2025_to_dl_s26,
            self.ept_dl_s26
        ]

    def get_total_points(self, team_database: TeamDatabase, teams: [Team]):
        return [
            self.ept_dl_s24_gs1.get_obtained_points(t_index) +
            self.ept_dl_s24_gs2.get_obtained_points(t_index) +
            self.ept_dl_s24.get_obtained_points(t_index) +
            self.dl_s24_to_esl_one_bkk_2024.get_change(t_index) +
            self.ept_esl_one_bkk_2024_gs.get_obtained_points(t_index) +
            self.ept_esl_one_bkk_2024.get_obtained_points(t_index) +
            self.esl_one_bkk_2024_to_dl_s25.get_change(t_index) +
            self.ept_dl_s25_gs1.get_obtained_points(t_index) +
            self.ept_dl_s25_gs2.get_obtained_points(t_index) +
            self.ept_dl_s25.get_obtained_points(t_index) +
            self.dl_s25_to_esl_one_ral_2025.get_change(t_index) +
            self.ept_esl_one_ral_2025_gs.get_obtained_points(t_index) +
            self.ept_esl_one_ral_2025.get_obtained_points(t_index) +
            self.esl_one_ral_2025_to_dl_s26.get_change(t_index) +
            self.ept_dl_s26_gs1.get_obtained_points(t_index) +
            self.ept_dl_s26_gs2.get_obtained_points(t_index) +
            self.ept_dl_s26.get_obtained_points(t_index)
            for t in teams
            if (t_index := team_database.get_team_index(t)) is not None
        ]


main()
