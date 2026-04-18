from typing import Tuple, Dict

from ortools.sat.python.cp_model import IntVar, CpModel

from ept import EptPairGroupStage, EptTournament, EptTournamentBase, EptStageBase
from metadata import Metadata
from stage import PairGroupStage, Tournament, DoubleElimination_8U8L2DSL1D, GroupStage
from teams import TeamDatabase, Team, Region


class DreamLeagueSeason29:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self.team_database = metadata.team_database

    def build(self) -> Tuple[EptTournamentBase, EptStageBase]:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database
        model: CpModel = metadata.model

        dl_s29_gs: PairGroupStage = PairGroupStage("dl_s29_gs", 8, 6, metadata)
        dl_s29_playoff: GroupStage = GroupStage("dl_s29_playoff", 12, 0, metadata)
        dl_s29: Tournament = Tournament("dl_s29", dl_s29_gs, metadata)

        # We don't know what happened to Falcons.  So 6 of these 7 were invited directly
        guaranteed_invites: [Team] = team_database.get_teams_by_names("Tundra Esports", "Team Yandex", "Xtreme Gaming",
                                                                      "Aurora Gaming", "PARIVISION", "Team Spirit", "Team Falcons")
        team_sum = 0
        for t in guaranteed_invites:
            team_index: int = team_database.get_team_index(t)
            team_sum += sum(dl_s29_gs.indicators[team_index])
        model.Add(team_sum == 6)

        qualified: [Team] = team_database.get_teams_by_names("Natus Vincere", "Virtus.pro", "Team Liquid",
                                                             "BetBoom Team", "GamerLegion", "Vici Gaming",
                                                             "REKONIX", "HEROIC")
        for g in qualified:
            team_index: int = team_database.get_team_index(g)
            model.Add(sum(dl_s29_gs.indicators[team_index]) == 1)

        dreamleague_division_2_season_4: [Team] = team_database.get_teams_by_names("Nigma Galaxy",
                                                                                   "Power Rangers (stack)", "1w Team",
                                                                                   "South America Rejects",
                                                                                   "Div 2 Team 1", "Div 2 Team 2")
        team_sum = 0
        for t in dreamleague_division_2_season_4:
            team_index: int = team_database.get_team_index(t)
            team_sum += sum(dl_s29_gs.indicators[team_index])
        model.Add(team_sum == 2)

        dl_s29_gs.bind_forward(dl_s29_playoff)
        ept_dl_s29_gs = EptPairGroupStage(dl_s29_gs, [600, 300, 150])

        ept_dl_s29 = EptTournament(dl_s29,
                                   ept_dl_s29_gs,
                                   [6000, 5000, 4000, 3200, 2200, 2200, 1000, 1000, 500, 500, 250, 250, 140, 140, 60,
                                    60],
                                   "DreamLeague Season 29",
                                   "DreamLeague/29",
                                   "/dreamleague",
                                   "2026-05-24",
                                   metadata)

        dl_s29_gs.build()
        dl_s29_playoff.build()
        dl_s29.build()
        ept_dl_s29_gs.build()
        ept_dl_s29.build()

        return ept_dl_s29, ept_dl_s29_gs

    def build_with_bracket(self) -> Tuple[EptTournamentBase, EptStageBase]:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database
        model: CpModel = metadata.model

        dl_s29_gs: PairGroupStage = PairGroupStage("dl_s29_gs", 8, 6, metadata)
        dl_s29_playoff: DoubleElimination_8U8L2DSL1D = DoubleElimination_8U8L2DSL1D("dl_s29_playoff", metadata)
        dl_s29: Tournament = Tournament("dl_s29", dl_s29_gs, metadata)

        # 6 of the top 8 of ESL One Birmingham 2026 will be in the top 6 at the end of the event
        guaranteed_invites: [Team] = team_database.get_teams_by_names("Tundra Esports", "Team Yandex", "Xtreme Gaming",
                                                                      "Aurora Gaming", "PARIVISION", "Team Spirit")
        qualified: [Team] = team_database.get_teams_by_names("Natus Vincere", "Virtus.pro")
        # eliminated_and_not_in_div_2_s4: [Team] = team_database.get_teams_by_names("OG", "Execration")
        eliminated_and_not_in_div_2_s4: [Team] = []
        for g in guaranteed_invites + qualified:
            team_index: int = team_database.get_team_index(g)
            model.Add(sum(dl_s29_gs.indicators[team_index]) == 1)

        region_slots: Dict[Region, int] = {
            Region.WEU: 1,
            Region.EEU: 1,
            Region.CN: 1,
            Region.SA: 1,
            Region.SEA: 1,
            Region.NA: 1
        }
        for region, slots in region_slots.items():
            team_sum: IntVar = 0
            for t in team_database.get_teams_by_region(region):
                if t in guaranteed_invites + qualified:
                    continue
                if t in eliminated_and_not_in_div_2_s4:
                    team_index: int = team_database.get_team_index(t)
                    model.Add(sum(dl_s29_gs.indicators[team_index]) == 0)
                else:
                    team_index: int = team_database.get_team_index(t)
                    team_sum += sum(dl_s29_gs.indicators[team_index])
            model.Add(team_sum >= slots)

        dl_s29_playoff.bind_backward(dl_s29_gs)
        dl_s29_gs.bind_forward(dl_s29_playoff)
        ept_dl_s29_gs = EptPairGroupStage(dl_s29_gs, [600, 300, 150])

        ept_dl_s29 = EptTournament(dl_s29,
                                   ept_dl_s29_gs,
                                   [6000, 5000, 4000, 3200, 2400, 2000, 1200, 800, 500, 500, 250, 250, 140, 140, 60,
                                    60],
                                   "DreamLeague Season 29",
                                   "DreamLeague/Season 29",
                                   "/dreamleague",
                                   "2026-05-24",
                                   metadata)

        dl_s29_gs.build()
        dl_s29_playoff.build()
        dl_s29.build()
        ept_dl_s29_gs.build()
        ept_dl_s29.build()

        return ept_dl_s29, ept_dl_s29_gs
