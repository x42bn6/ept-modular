from typing import Tuple

from ept import EptPairGroupStage, EptTournament, SolvedEptStage, SolvedEptTournament, EptStageBase, EptTournamentBase
from metadata import Metadata
from stage import PairGroupStage, DoubleElimination_4U4L2DSL1D, Tournament, Root
from teams import TeamDatabase, Team


class EslOneRaleigh2025:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self.team_database = metadata.team_database

    def build(self) -> Tuple[EptTournamentBase, EptStageBase]:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database

        esl_one_ral_2025_gs: PairGroupStage = PairGroupStage("esl_one_ral_2025_gs", 6, 4, metadata)
        esl_one_ral_2025_playoff: DoubleElimination_4U4L2DSL1D = DoubleElimination_4U4L2DSL1D(
            "esl_one_ral_2025_playoff", metadata)
        esl_one_ral_2025: Tournament = Tournament("esl_one_ral_2025", esl_one_ral_2025_gs, metadata)

        esl_one_ral_2025_gs.group_a = team_database.get_teams_by_names(
            "Nigma Galaxy", "PARIVISION", "Shopify Rebellion", "Talon Esports", "Team Liquid", "Team Spirit")
        esl_one_ral_2025_gs.group_b = team_database.get_teams_by_names(
            "AVULUS", "BetBoom Team", "HEROIC", "Team Falcons", "Team Tidebound", "Tundra Esports")

        esl_one_ral_2025_playoff.bind_backward(esl_one_ral_2025_gs)
        esl_one_ral_2025_gs.bind_forward(esl_one_ral_2025_playoff)

        ept_esl_one_ral_2025_gs = EptPairGroupStage(esl_one_ral_2025_gs, [640])
        ept_esl_one_ral_2025 = EptTournament(esl_one_ral_2025, ept_esl_one_ral_2025_gs,
                                             [6400, 4800, 4000, 3200, 2240, 2240, 1040, 1040, 560, 560, 280, 280],
                                             "ESL One Raleigh 2025",
                                             "ESL One/Raleigh/2025",
                                             "/esl_one",
                                             "2025-04-13",
                                             metadata)

        esl_one_ral_2025_gs.team_can_finish_between("PARIVISION", 1, 2)
        esl_one_ral_2025_gs.team_can_finish_between("Team Spirit", 3, 4)
        esl_one_ral_2025_gs.team_can_finish_between("Team Liquid", 5, 6)
        esl_one_ral_2025_gs.team_can_finish_between("Nigma Galaxy", 7, 8)
        esl_one_ral_2025_gs.team_can_finish_between("Shopify Rebellion", 9, 10)
        esl_one_ral_2025_gs.team_can_finish_between("Talon Esports", 11, 12)

        esl_one_ral_2025_gs.team_can_finish_between("Team Falcons", 1, 2)
        esl_one_ral_2025_gs.team_can_finish_between("Tundra Esports", 3, 4)
        esl_one_ral_2025_gs.team_can_finish_between("BetBoom Team", 5, 6)
        esl_one_ral_2025_gs.team_can_finish_between("AVULUS", 7, 8)
        esl_one_ral_2025_gs.team_can_finish_between("Team Tidebound", 9, 10)
        esl_one_ral_2025_gs.team_can_finish_between("HEROIC", 11, 12)

        esl_one_ral_2025_playoff.ubsf_1.set_winner("Tundra Esports")
        esl_one_ral_2025_playoff.ubsf_2.set_winner("Team Spirit")

        esl_one_ral_2025_playoff.ubf.set_winner("Team Spirit")

        esl_one_ral_2025_playoff.lbr1_1.set_winner("Team Liquid")
        esl_one_ral_2025_playoff.lbr1_2.set_winner("BetBoom Team")

        esl_one_ral_2025_playoff.lbqf_1.set_winner("PARIVISION")
        esl_one_ral_2025_playoff.lbqf_2.set_winner("BetBoom Team")

        esl_one_ral_2025_playoff.lbsf.set_winner("PARIVISION")

        esl_one_ral_2025_playoff.lbf.set_winner("PARIVISION")

        esl_one_ral_2025_playoff.gf.set_winner("PARIVISION")

        esl_one_ral_2025_gs.build()
        esl_one_ral_2025_playoff.build()
        esl_one_ral_2025.build()
        ept_esl_one_ral_2025_gs.build()
        ept_esl_one_ral_2025.build()

        return ept_esl_one_ral_2025, ept_esl_one_ral_2025_gs


class EslOneRaleigh2025Solved:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata

    def build(self) -> Tuple[EptTournamentBase, EptStageBase]:
        metadata: Metadata = self.metadata

        esl_one_ral_2025_gs: SolvedEptStage = SolvedEptStage("esl_one_ral_2025_gs", 12, [480], metadata)
        esl_one_ral_2025: SolvedEptTournament = SolvedEptTournament("esl_one_ral_2025", esl_one_ral_2025_gs,
                                                                    [6400, 4800, 4000, 3200, 2240, 2240, 1040, 1040,
                                                                     560, 560, 280, 280],
                                                                    "ESL One Raleigh 2025",
                                                                    "ESL One/Raleigh/2025",
                                                                    "/esl_one",
                                                                    "2025-04-13",
                                                                    metadata)

        esl_one_ral_2025_gs.set_position("PARIVISION", 1)
        esl_one_ral_2025_gs.set_position("Team Spirit", 3)
        esl_one_ral_2025_gs.set_position("Team Liquid", 5)
        esl_one_ral_2025_gs.set_position("Nigma Galaxy", 7)
        esl_one_ral_2025_gs.set_position("Shopify Rebellion", 9)
        esl_one_ral_2025_gs.set_position("Talon Esports", 11)

        esl_one_ral_2025_gs.set_position("Team Falcons", 2)
        esl_one_ral_2025_gs.set_position("Tundra Esports", 4)
        esl_one_ral_2025_gs.set_position("BetBoom Team", 6)
        esl_one_ral_2025_gs.set_position("AVULUS", 8)
        esl_one_ral_2025_gs.set_position("Team Tidebound", 10)
        esl_one_ral_2025_gs.set_position("HEROIC", 12)

        esl_one_ral_2025.set_position("PARIVISION", 1)
        esl_one_ral_2025.set_position("Team Spirit", 2)
        esl_one_ral_2025.set_position("Tundra Esports", 3)
        esl_one_ral_2025.set_position("BetBoom Team", 4)
        esl_one_ral_2025.set_position("Team Liquid", 5)
        esl_one_ral_2025.set_position("Team Falcons", 6)
        esl_one_ral_2025.set_position("AVULUS", 7)
        esl_one_ral_2025.set_position("Nigma Galaxy", 8)
        esl_one_ral_2025.set_position("Shopify Rebellion", 9)
        esl_one_ral_2025.set_position("Team Tidebound", 10)
        esl_one_ral_2025.set_position("Talon Esports", 11)
        esl_one_ral_2025.set_position("HEROIC", 12)

        return esl_one_ral_2025, esl_one_ral_2025_gs
