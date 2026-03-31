from typing import Tuple

from ept import EptPairGroupStage, EptTournament, SolvedEptStage, SolvedEptTournament, EptStageBase, EptTournamentBase
from metadata import Metadata
from stage import PairGroupStage, DoubleElimination_4U4L2DSL1D, Tournament
from teams import TeamDatabase


class EslOneBirmingham2026:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self.team_database = metadata.team_database

    def build(self) -> Tuple[EptTournamentBase, EptStageBase]:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database

        esl_one_bir_2026_gs: PairGroupStage = PairGroupStage("esl_one_bir_2026_gs", 8, 4, metadata)
        esl_one_bir_2026_playoff: DoubleElimination_4U4L2DSL1D = DoubleElimination_4U4L2DSL1D(
            "esl_one_bir_2026_playoff", metadata)
        esl_one_bir_2026: Tournament = Tournament("esl_one_bir_2026", esl_one_bir_2026_gs, metadata)

        esl_one_bir_2026_gs.group_a = team_database.get_teams_by_names(
            "Team Yandex", "Tundra Esports", "MOUZ", "PARIVISION", "GamerLegion", "BetBoom Team", "Yakult Brothers",
            "REKONIX")
        esl_one_bir_2026_gs.group_b = team_database.get_teams_by_names(
            "Aurora Gaming", "Team Spirit", "Team Falcons", "Xtreme Gaming", "Virtus.pro", "paiN Gaming", "OG",
            "Nigma Galaxy")

        esl_one_bir_2026_playoff.bind_backward(esl_one_bir_2026_gs)
        esl_one_bir_2026_gs.bind_forward(esl_one_bir_2026_playoff)

        ept_esl_one_bir_2026_gs = EptPairGroupStage(esl_one_bir_2026_gs, [800])
        ept_esl_one_bir_2026 = EptTournament(esl_one_bir_2026, ept_esl_one_bir_2026_gs,
                                             [8000, 6000, 5000, 4000, 2800, 2800, 1300, 1300, 700, 700, 350, 350, 180,
                                              180, 100, 100],
                                             "ESL One Birmingham 2026",
                                             "ESL One/Birmingham/2026",
                                             "/esl_one",
                                             "2026-03-29",
                                             metadata)

        esl_one_bir_2026_gs.team_can_finish_between("Team Yandex", 1, 2)
        esl_one_bir_2026_gs.team_can_finish_between("Tundra Esports", 3, 4)
        esl_one_bir_2026_gs.team_can_finish_between("MOUZ", 5, 6)
        esl_one_bir_2026_gs.team_can_finish_between("PARIVISION", 7, 8)
        esl_one_bir_2026_gs.team_can_finish_between("GamerLegion", 9, 10)
        esl_one_bir_2026_gs.team_can_finish_between("BetBoom Team", 11, 12)
        esl_one_bir_2026_gs.team_can_finish_between("Yakult Brothers", 13, 14)
        esl_one_bir_2026_gs.team_can_finish_between("REKONIX", 15, 16)

        esl_one_bir_2026_gs.team_can_finish_between("Aurora Gaming", 1, 2)
        esl_one_bir_2026_gs.team_can_finish_between("Team Spirit", 3, 4)
        esl_one_bir_2026_gs.team_can_finish_between("Team Falcons", 5, 6)
        esl_one_bir_2026_gs.team_can_finish_between("Xtreme Gaming", 7, 8)
        esl_one_bir_2026_gs.team_can_finish_between("Virtus.pro", 9, 10)
        esl_one_bir_2026_gs.team_can_finish_between("paiN Gaming", 11, 12)
        esl_one_bir_2026_gs.team_can_finish_between("OG", 13, 14)
        esl_one_bir_2026_gs.team_can_finish_between("Nigma Galaxy", 15, 16)

        esl_one_bir_2026_playoff.ubsf_1.set_winner("Team Yandex")
        esl_one_bir_2026_playoff.ubsf_2.set_winner("Tundra Esports")

        esl_one_bir_2026_playoff.ubf.set_winner("Tundra Esports")

        esl_one_bir_2026_playoff.lbr1_1.set_winner("Xtreme Gaming")
        esl_one_bir_2026_playoff.lbr1_2.set_winner("PARIVISION")

        esl_one_bir_2026_playoff.lbqf_1.set_winner("Xtreme Gaming")
        esl_one_bir_2026_playoff.lbqf_2.set_winner("PARIVISION")

        esl_one_bir_2026_playoff.lbsf.set_winner("Xtreme Gaming")

        esl_one_bir_2026_playoff.lbf.set_winner("Team Yandex")

        esl_one_bir_2026_playoff.gf.set_winner("Tundra Esports")

        esl_one_bir_2026_gs.build()
        esl_one_bir_2026_playoff.build()
        esl_one_bir_2026.build()
        ept_esl_one_bir_2026_gs.build()
        ept_esl_one_bir_2026.build()

        return ept_esl_one_bir_2026, ept_esl_one_bir_2026_gs


class EslOneBirmingham2026Solved:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata

    def build(self) -> Tuple[EptTournamentBase, EptStageBase]:
        metadata: Metadata = self.metadata

        esl_one_bir_2026_gs: SolvedEptStage = SolvedEptStage("esl_one_bir_2026_gs", 16, [800, 800], metadata)
        esl_one_bir_2026: SolvedEptTournament = SolvedEptTournament("esl_one_bir_2026", esl_one_bir_2026_gs,
                                                                    [8000, 6000, 5000, 4000, 2800, 2800, 1300, 1300,
                                                                     700, 700, 350, 350, 180, 180, 100, 100],
                                                                    "ESL One Birmingham 2026",
                                                                    "ESL One/Birmingham/2026",
                                                                    "/esl_one",
                                                                    "2026-03-29",
                                                                    metadata)

        esl_one_bir_2026_gs.set_position("Team Yandex", 1)
        esl_one_bir_2026_gs.set_position("Tundra Esports", 3)
        esl_one_bir_2026_gs.set_position("MOUZ", 5)
        esl_one_bir_2026_gs.set_position("PARIVISION", 7)
        esl_one_bir_2026_gs.set_position("GamerLegion", 9)
        esl_one_bir_2026_gs.set_position("BetBoom Team", 11)
        esl_one_bir_2026_gs.set_position("Yakult Brothers", 13)
        esl_one_bir_2026_gs.set_position("REKONIX", 15)

        esl_one_bir_2026_gs.set_position("Aurora Gaming", 2)
        esl_one_bir_2026_gs.set_position("Team Spirit", 4)
        esl_one_bir_2026_gs.set_position("Team Falcons", 6)
        esl_one_bir_2026_gs.set_position("Xtreme Gaming", 8)
        esl_one_bir_2026_gs.set_position("Virtus.pro", 10)
        esl_one_bir_2026_gs.set_position("paiN Gaming", 12)
        esl_one_bir_2026_gs.set_position("OG", 14)
        esl_one_bir_2026_gs.set_position("Nigma Galaxy", 16)

        esl_one_bir_2026.set_position("Tundra Esports", 1)
        esl_one_bir_2026.set_position("Team Yandex", 2)
        esl_one_bir_2026.set_position("Xtreme Gaming", 3)
        esl_one_bir_2026.set_position("PARIVISION", 4)
        esl_one_bir_2026.set_position("Team Spirit", 5)
        esl_one_bir_2026.set_position("Aurora Gaming", 6)
        esl_one_bir_2026.set_position("MOUZ", 7)
        esl_one_bir_2026.set_position("Team Falcons", 8)
        esl_one_bir_2026.set_position("GamerLegion", 9)
        esl_one_bir_2026.set_position("Virtus.pro", 10)
        esl_one_bir_2026.set_position("BetBoom Team", 11)
        esl_one_bir_2026.set_position("paiN Gaming", 12)
        esl_one_bir_2026.set_position("Yakult Brothers", 13)
        esl_one_bir_2026.set_position("OG", 14)
        esl_one_bir_2026.set_position("REKONIX", 15)
        esl_one_bir_2026.set_position("Nigma Galaxy", 16)

        return esl_one_bir_2026, esl_one_bir_2026_gs
