from typing import Tuple

from ept import EptPairGroupStage, EptGroupStage, EptTournament, EptStageBase, EptTournamentBase, SolvedEptStage, \
    SolvedEptTournament
from metadata import Metadata
from stage import PairGroupStage, GroupStage, DoubleElimination_2U2L1D, Tournament
from teams import TeamDatabase


class DreamLeagueSeason25:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self.team_database = metadata.team_database

    def build(self) -> Tuple[EptTournamentBase, EptStageBase, EptStageBase]:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database

        dl_s25_gs1: PairGroupStage = PairGroupStage("dl_s25_gs1", 8, 4, metadata)
        dl_s25_gs2: GroupStage = GroupStage("dl_s25_gs2", 8, 4, metadata)
        dl_s25_playoff: DoubleElimination_2U2L1D = DoubleElimination_2U2L1D("dl_s25_playoff", metadata)
        dl_s25: Tournament = Tournament("dl_s25", dl_s25_gs1, metadata)
        dl_s25_gs1.group_a = team_database.get_teams_by_names("Tundra Esports", "BetBoom Team", "Team Falcons",
                                                              "HEROIC", "Shopify Rebellion",
                                                              "Moodeng Warriors", "Xtreme Gaming", "9Pandas")
        dl_s25_gs1.group_b = team_database.get_teams_by_names("Team Spirit", "Chimera Esports", "PARIVISION",
                                                              "Gaimin Gladiators", "Team Liquid", "Yakult Brothers",
                                                              "BOOM Esports", "AVULUS")
        dl_s25_gs1.bind_forward(dl_s25_gs2)
        dl_s25_playoff.bind_backward(dl_s25_gs2)
        dl_s25_gs2.bind_forward(dl_s25_playoff)
        ept_dl_s25_gs1 = EptPairGroupStage(dl_s25_gs1, [420, 210, 105])
        ept_dl_s25_gs2 = EptGroupStage(dl_s25_gs2, [420])
        ept_dl_s25_gs1.bind_next_ept_stage(ept_dl_s25_gs2)
        ept_dl_s25 = EptTournament(dl_s25,
                                   ept_dl_s25_gs1,
                                   [4200, 3500, 2800, 2240, 1680, 1400, 840, 560, 350, 350, 175, 175, 98, 98, 42, 42],
                                   "DreamLeague Season 25",
                                   "DreamLeague/Season 25",
                                   "/dreamleague",
                                   "2025-03-02",
                                   metadata)

        dl_s25_gs1.team_can_finish_between("Tundra Esports", 1, 2)
        dl_s25_gs1.team_can_finish_between("BetBoom Team", 3, 4)
        dl_s25_gs1.team_can_finish_between("Team Falcons", 5, 6)
        dl_s25_gs1.team_can_finish_between("HEROIC", 7, 8)
        dl_s25_gs1.team_can_finish_between("Shopify Rebellion", 9, 10)
        dl_s25_gs1.team_can_finish_between("Moodeng Warriors", 11, 12)
        dl_s25_gs1.team_can_finish_between("Xtreme Gaming", 13, 14)
        dl_s25_gs1.team_can_finish_between("9Pandas", 15, 16)

        dl_s25_gs1.team_can_finish_between("Team Spirit", 1, 2)
        dl_s25_gs1.team_can_finish_between("Chimera Esports", 3, 4)
        dl_s25_gs1.team_can_finish_between("PARIVISION", 5, 6)
        dl_s25_gs1.team_can_finish_between("Team Liquid", 7, 8)
        dl_s25_gs1.team_can_finish_between("Yakult Brothers", 9, 10)
        dl_s25_gs1.team_can_finish_between("Gaimin Gladiators", 11, 12)
        dl_s25_gs1.team_can_finish_between("BOOM Esports", 13, 14)
        dl_s25_gs1.team_can_finish_between("AVULUS", 15, 16)

        dl_s25_gs2.team_can_finish_between("PARIVISION", 1, 1)
        dl_s25_gs2.team_can_finish_between("Tundra Esports", 2, 2)
        dl_s25_gs2.team_can_finish_between("Team Spirit", 3, 3)
        dl_s25_gs2.team_can_finish_between("Chimera Esports", 4, 4)
        dl_s25_gs2.team_can_finish_between("Team Falcons", 5, 5)
        dl_s25_gs2.team_can_finish_between("BetBoom Team", 6, 6)
        dl_s25_gs2.team_can_finish_between("Team Liquid", 7, 7)
        dl_s25_gs2.team_can_finish_between("HEROIC", 8, 8)

        dl_s25_playoff.lbsf.set_winner("Team Spirit")
        dl_s25_playoff.ubf.set_winner("Tundra Esports")
        dl_s25_playoff.lbf.set_winner("Team Spirit")
        dl_s25_playoff.gf.set_winner("Team Spirit")

        dl_s25_gs1.build()
        dl_s25_gs2.build()
        dl_s25_playoff.build()
        dl_s25.build()
        ept_dl_s25_gs1.build()
        ept_dl_s25_gs2.build()
        ept_dl_s25.build()

        return ept_dl_s25, ept_dl_s25_gs1, ept_dl_s25_gs2


class DreamLeagueSeason25Solved:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata

    def build(self) -> Tuple[EptTournamentBase, EptStageBase, EptStageBase]:
        metadata: Metadata = self.metadata

        dl_s25_gs1: SolvedEptStage = SolvedEptStage("dl_s25_gs1", 16, [420, 420, 210, 210, 105, 105], metadata)
        dl_s25_gs2: SolvedEptStage = SolvedEptStage("dl_s25_gs2", 8, [420], metadata)
        dl_s25_gs1.bind_next_ept_stage(dl_s25_gs2)
        dl_s25: SolvedEptTournament = SolvedEptTournament("dl_s25",
                                                          dl_s25_gs1,
                                                          [4200, 3500, 2800, 2240, 1680, 1400, 840, 560, 350, 350, 175,
                                                           175, 98, 98, 42, 42],
                                                          "DreamLeague Season 25",
                                                          "DreamLeague/Season 25",
                                                          "/dreamleague",
                                                          "2025-03-02",
                                                          metadata)

        dl_s25_gs1.set_position("Tundra Esports", 1)
        dl_s25_gs1.set_position("BetBoom Team", 3)
        dl_s25_gs1.set_position("Team Falcons", 5)
        dl_s25_gs1.set_position("HEROIC", 7)
        dl_s25_gs1.set_position("Shopify Rebellion", 9)
        dl_s25_gs1.set_position("Moodeng Warriors", 11)
        dl_s25_gs1.set_position("Xtreme Gaming", 13)
        dl_s25_gs1.set_position("9Pandas", 15)

        dl_s25_gs1.set_position("Team Spirit", 2)
        dl_s25_gs1.set_position("Chimera Esports", 4)
        dl_s25_gs1.set_position("PARIVISION", 6)
        dl_s25_gs1.set_position("Team Liquid", 8)
        dl_s25_gs1.set_position("Yakult Brothers", 10)
        dl_s25_gs1.set_position("Gaimin Gladiators", 12)
        dl_s25_gs1.set_position("BOOM Esports", 14)
        dl_s25_gs1.set_position("AVULUS", 16)

        dl_s25_gs2.set_position("PARIVISION", 1)
        dl_s25_gs2.set_position("Tundra Esports", 2)
        dl_s25_gs2.set_position("Team Spirit", 3)
        dl_s25_gs2.set_position("Chimera Esports", 4)
        dl_s25_gs2.set_position("Team Falcons", 5)
        dl_s25_gs2.set_position("BetBoom Team", 6)
        dl_s25_gs2.set_position("Team Liquid", 7)
        dl_s25_gs2.set_position("HEROIC", 8)

        dl_s25.set_position("Team Spirit", 1)
        dl_s25.set_position("Tundra Esports", 2)
        dl_s25.set_position("PARIVISION", 3)
        dl_s25.set_position("Chimera Esports", 4)
        dl_s25.set_position("Team Falcons", 5)
        dl_s25.set_position("BetBoom Team", 6)
        dl_s25.set_position("Team Liquid", 7)
        dl_s25.set_position("HEROIC", 8)
        dl_s25.set_position("Shopify Rebellion", 9)
        dl_s25.set_position("Yakult Brothers", 10)
        dl_s25.set_position("Moodeng Warriors", 11)
        dl_s25.set_position("Gaimin Gladiators", 12)
        dl_s25.set_position("Xtreme Gaming", 13)
        dl_s25.set_position("BOOM Esports", 14)
        dl_s25.set_position("9Pandas", 15)
        dl_s25.set_position("AVULUS", 16)

        return dl_s25, dl_s25_gs1, dl_s25_gs2
