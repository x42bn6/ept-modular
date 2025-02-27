from typing import Tuple

from ept import EptPairGroupStage, EptGroupStage, EptTournament, SolvedEptStage, SolvedEptTournament, EptStageBase, \
    EptTournamentBase
from metadata import Metadata
from stage import PairGroupStage, GroupStage, DoubleElimination_2U2L1D, Tournament
from teams import TeamDatabase


class DreamLeagueSeason24:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self.team_database = metadata.team_database

    def build(self) -> Tuple[EptTournamentBase, EptStageBase, EptStageBase]:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database

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
                                   "DreamLeague Season 24",
                                   "DreamLeague/Season 24",
                                   "/dreamleague",
                                   "2024-11-10",
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

        return ept_dl_s24, ept_dl_s24_gs1, ept_dl_s24_gs2


class DreamLeagueSeason24Solved:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata

    def build(self) -> Tuple[EptTournamentBase, EptStageBase, EptStageBase]:
        metadata: Metadata = self.metadata

        dl_s24_gs1: SolvedEptStage = SolvedEptStage("dl_s24_gs2", 16, [300, 300, 150, 150, 75, 75], metadata)
        dl_s24_gs2: SolvedEptStage = SolvedEptStage("dl_s24_gs2", 8, [300], metadata)
        dl_s24_gs1.bind_next_ept_stage(dl_s24_gs2)
        dl_s24: SolvedEptTournament = SolvedEptTournament("dl_s24",
                                                          dl_s24_gs1,
                                                          [3000, 2500, 2000, 1600, 1200, 1000, 600, 400, 250, 250, 125,
                                                           125, 70, 70, 30, 30],
                                                          "DreamLeague Season 24",
                                                          "DreamLeague/Season 24",
                                                          "/dreamleague",
                                                          "2024-11-10",
                                                          metadata)

        dl_s24_gs1.set_position("PARIVISION", 1)
        dl_s24_gs1.set_position("Team Liquid", 3)
        dl_s24_gs1.set_position("Xtreme Gaming", 5)
        dl_s24_gs1.set_position("BetBoom Team", 7)
        dl_s24_gs1.set_position("Gaimin Gladiators", 9)
        dl_s24_gs1.set_position("AVULUS", 11)
        dl_s24_gs1.set_position("Nigma Galaxy", 13)
        dl_s24_gs1.set_position("Nouns Esports", 15)

        dl_s24_gs1.set_position("Team Falcons", 2)
        dl_s24_gs1.set_position("Team Waska", 4)
        dl_s24_gs1.set_position("Tundra Esports", 6)
        dl_s24_gs1.set_position("Team Spirit", 8)
        dl_s24_gs1.set_position("Talon Esports", 10)
        dl_s24_gs1.set_position("Azure Ray", 12)
        dl_s24_gs1.set_position("HEROIC", 14)
        dl_s24_gs1.set_position("Palianytsia", 16)

        dl_s24_gs2.set_position("BetBoom Team", 1)
        dl_s24_gs2.set_position("Team Spirit", 2)
        dl_s24_gs2.set_position("PARIVISION", 3)
        dl_s24_gs2.set_position("Team Falcons", 4)
        dl_s24_gs2.set_position("Tundra Esports", 5)
        dl_s24_gs2.set_position("Team Liquid", 6)
        dl_s24_gs2.set_position("Xtreme Gaming", 7)
        dl_s24_gs2.set_position("Team Waska", 8)

        dl_s24.set_position("Team Falcons", 1)
        dl_s24.set_position("BetBoom Team", 2)
        dl_s24.set_position("Team Spirit", 3)
        dl_s24.set_position("PARIVISION", 4)
        dl_s24.set_position("Tundra Esports", 5)
        dl_s24.set_position("Team Liquid", 6)
        dl_s24.set_position("Xtreme Gaming", 7)
        dl_s24.set_position("Team Waska", 8)
        dl_s24.set_position("Gaimin Gladiators", 9)
        dl_s24.set_position("Talon Esports", 10)
        dl_s24.set_position("AVULUS", 11)
        dl_s24.set_position("Azure Ray", 12)
        dl_s24.set_position("Nigma Galaxy", 13)
        dl_s24.set_position("HEROIC", 14)
        dl_s24.set_position("Nouns Esports", 15)
        dl_s24.set_position("Palianytsia", 16)

        return dl_s24, dl_s24_gs1, dl_s24_gs2
