from typing import Tuple

from ept import EptPairGroupStage, EptGroupStage, EptTournament, EptTournamentBase, EptStageBase
from metadata import Metadata
from stage import PairGroupStage, GroupStage, DoubleElimination_2U2L1D, Tournament
from teams import TeamDatabase


class DreamLeagueSeason26:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self.team_database = metadata.team_database

    def build(self) -> Tuple[EptTournamentBase, EptStageBase, EptStageBase]:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database

        dl_s26_gs1: PairGroupStage = PairGroupStage("dl_s26_gs1", 8, 4, metadata)
        dl_s26_gs2: GroupStage = GroupStage("dl_s26_gs2", 8, 4, metadata)
        dl_s26_playoff: DoubleElimination_2U2L1D = DoubleElimination_2U2L1D("dl_s26_playoff", metadata)
        dl_s26: Tournament = Tournament("dl_s26", dl_s26_gs1, metadata)
        dl_s26_gs1.group_a = team_database.get_teams_by_names("Aurora Gaming", "BetBoom Team", "BOOM Esports",
                                                              "Nigma Galaxy", "OG.LATAM", "Shopify Rebellion",
                                                              "Team Liquid", "Xtreme Gaming")
        dl_s26_gs1.group_b = team_database.get_teams_by_names("AVULUS", "Edge (team)", "Gaimin Gladiators",
                                                              "NAVI Junior", "PARIVISION", "Talon Esports",
                                                              "Team Falcons", "Yakult Brothers")

        dl_s26_gs1.bind_forward(dl_s26_gs2)
        dl_s26_playoff.bind_backward(dl_s26_gs2)
        dl_s26_gs2.bind_forward(dl_s26_playoff)
        ept_dl_s26_gs1 = EptPairGroupStage(dl_s26_gs1, [600, 300, 150])
        ept_dl_s26_gs2 = EptGroupStage(dl_s26_gs2, [600])
        ept_dl_s26_gs1.bind_next_ept_stage(ept_dl_s26_gs2)

        ept_dl_s26 = EptTournament(dl_s26,
                                   ept_dl_s26_gs1,
                                   [6000, 5000, 4000, 3200, 2400, 2000, 1200, 800, 500, 500, 250, 250, 140, 140, 60,
                                    60],
                                   "DreamLeague Season 26",
                                   "DreamLeague/Season 26",
                                   "/dreamleague",
                                   "2025-06-01",
                                   metadata)

        dl_s26_gs1.team_can_finish_between("Aurora Gaming", 1, 2)
        dl_s26_gs1.team_can_finish_between("Nigma Galaxy", 3, 4)
        dl_s26_gs1.team_can_finish_between("BetBoom Team", 5, 8)
        dl_s26_gs1.team_can_finish_between("Team Liquid", 5, 8)
        dl_s26_gs1.team_can_finish_between("Shopify Rebellion", 9, 10)
        dl_s26_gs1.team_can_finish_between("Xtreme Gaming", 11, 15)
        dl_s26_gs1.team_can_finish_between("BOOM Esports", 11, 15)
        dl_s26_gs1.team_can_finish_between("OG.LATAM", 12, 16)

        dl_s26_gs1.team_can_finish_between("PARIVISION", 1, 2)
        dl_s26_gs1.team_can_finish_between("Yakult Brothers", 3, 4)
        dl_s26_gs1.team_can_finish_between("Talon Esports", 5, 6)
        dl_s26_gs1.team_can_finish_between("Gaimin Gladiators", 7, 8)
        dl_s26_gs1.team_can_finish_between("Team Falcons", 9, 10)
        dl_s26_gs1.team_can_finish_between("NAVI Junior", 11, 12)
        dl_s26_gs1.team_can_finish_between("AVULUS", 13, 14)
        dl_s26_gs1.team_can_finish_between("Edge (team)", 15, 16)

        dl_s26_gs2.team_can_finish_between("PARIVISION", 1, 1)
        dl_s26_gs2.team_can_finish_between("BetBoom Team", 2, 2)
        dl_s26_gs2.team_can_finish_between("Talon Esports", 3, 3)
        dl_s26_gs2.team_can_finish_between("Aurora Gaming", 4, 4)
        dl_s26_gs2.team_can_finish_between("Gaimin Gladiators", 5, 5)
        dl_s26_gs2.team_can_finish_between("Yakult Brothers", 6, 6)
        dl_s26_gs2.team_can_finish_between("Nigma Galaxy", 7, 7)
        dl_s26_gs2.team_can_finish_between("Team Liquid", 8, 8)

        dl_s26_playoff.lbsf.set_winner("Talon Esports")
        dl_s26_playoff.ubf.set_winner("PARIVISION")
        dl_s26_playoff.lbf.set_winner("BetBoom Team")
        dl_s26_playoff.gf.set_winner("PARIVISION")

        dl_s26_gs1.build()
        dl_s26_gs2.build()
        dl_s26_playoff.build()
        dl_s26.build()
        ept_dl_s26_gs1.build()
        ept_dl_s26_gs2.build()
        ept_dl_s26.build()

        return ept_dl_s26, ept_dl_s26_gs1, ept_dl_s26_gs2
