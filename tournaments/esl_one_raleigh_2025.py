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

        esl_one_ral_2025_gs.build()
        esl_one_ral_2025_playoff.build()
        esl_one_ral_2025.build()
        ept_esl_one_ral_2025_gs.build()
        ept_esl_one_ral_2025.build()

        return ept_esl_one_ral_2025, ept_esl_one_ral_2025_gs

