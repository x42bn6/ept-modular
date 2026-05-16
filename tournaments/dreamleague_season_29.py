from typing import Tuple

from ept import EptPairGroupStage, EptTournament, EptTournamentBase, EptStageBase
from metadata import Metadata
from stage import PairGroupStage, Tournament, DoubleElimination_8U8L2DSL1D, GroupStage
from teams import TeamDatabase


class DreamLeagueSeason29:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self.team_database = metadata.team_database

    def build(self) -> Tuple[EptTournamentBase, EptStageBase]:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database

        dl_s29_gs: PairGroupStage = PairGroupStage("dl_s29_gs", 8, 6, metadata)
        dl_s29_playoff: GroupStage = GroupStage("dl_s29_playoff", 12, 0, metadata)
        dl_s29: Tournament = Tournament("dl_s29", dl_s29_gs, metadata)
        dl_s29_gs.group_a = team_database.get_teams_by_names("Aurora Gaming", "ex-HEROIC", "GamerLegion", "Team Falcons", "Team Liquid", "Team Spirit", "Vici Gaming", "Virtus.pro")
        dl_s29_gs.group_b = team_database.get_teams_by_names("BetBoom Team", "Natus Vincere", "Nigma Galaxy", "PARIVISION", "PlayTime", "REKONIX", "Tundra Esports", "Xtreme Gaming")

        dl_s29_gs.bind_forward(dl_s29_playoff)
        ept_dl_s29_gs = EptPairGroupStage(dl_s29_gs, [600, 300, 150])

        ept_dl_s29 = EptTournament(dl_s29,
                                   ept_dl_s29_gs,
                                   [6000, 5000, 4000, 3200, 2200, 2200, 1000, 1000, 375, 375, 375, 375, 140, 140, 60,
                                    60],
                                   "DreamLeague Season 29",
                                   "DreamLeague/29",
                                   "/dreamleague",
                                   "2026-05-24",
                                   metadata)

        dl_s29_gs.team_can_finish_between("Team Falcons", 1, 6)
        dl_s29_gs.team_can_finish_between("Team Spirit", 1, 6)
        dl_s29_gs.team_can_finish_between("Team Liquid", 5, 8)
        dl_s29_gs.team_can_finish_between("Aurora Gaming", 5, 12)
        dl_s29_gs.team_can_finish_between("Vici Gaming", 7, 16)
        dl_s29_gs.team_can_finish_between("Virtus.pro", 7, 16)
        dl_s29_gs.team_can_finish_between("ex-HEROIC", 9, 16)
        dl_s29_gs.team_can_finish_between("GamerLegion", 9, 16)

        dl_s29_gs.team_can_finish_between("Natus Vincere", 1, 4)
        dl_s29_gs.team_can_finish_between("PARIVISION", 1, 4)
        dl_s29_gs.team_can_finish_between("BetBoom Team", 5, 14)
        dl_s29_gs.team_can_finish_between("PlayTime", 5, 14)
        dl_s29_gs.team_can_finish_between("Xtreme Gaming", 5, 14)
        dl_s29_gs.team_can_finish_between("Nigma Galaxy", 5, 16)
        dl_s29_gs.team_can_finish_between("Tundra Esports", 5, 16)
        dl_s29_gs.team_can_finish_between("REKONIX", 11, 16)

        dl_s29_gs.build()
        dl_s29_playoff.build()
        dl_s29.build()
        ept_dl_s29_gs.build()
        ept_dl_s29.build()

        return ept_dl_s29, ept_dl_s29_gs

    def build_with_bracket(self) -> Tuple[EptTournamentBase, EptStageBase]:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database

        dl_s29_gs: PairGroupStage = PairGroupStage("dl_s29_gs", 8, 6, metadata)
        dl_s29_playoff: DoubleElimination_8U8L2DSL1D = DoubleElimination_8U8L2DSL1D("dl_s29_playoff", metadata)
        dl_s29: Tournament = Tournament("dl_s29", dl_s29_gs, metadata)
        dl_s29_gs.group_a = team_database.get_teams_by_names("Aurora Gaming", "ex-HEROIC", "GamerLegion", "Team Falcons", "Team Liquid", "Team Spirit", "Vici Gaming", "Virtus.pro")
        dl_s29_gs.group_b = team_database.get_teams_by_names("BetBoom Team", "Natus Vincere", "Nigma Galaxy", "PARIVISION", "PlayTime", "REKONIX", "Tundra Esports", "Xtreme Gaming")

        dl_s29_playoff.bind_backward(dl_s29_gs)
        dl_s29_gs.bind_forward(dl_s29_playoff)
        ept_dl_s29_gs = EptPairGroupStage(dl_s29_gs, [600, 300, 150])

        ept_dl_s29 = EptTournament(dl_s29,
                                   ept_dl_s29_gs,
                                   [6000, 5000, 4000, 3200, 2200, 2200, 1000, 1000, 375, 375, 375, 375, 140, 140, 60,
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
