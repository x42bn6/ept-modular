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

        participating_teams: [Team] = team_database.get_teams_by_names("PARIVISION", "BetBoom Team", "Team Falcons", "Team Liquid",
                                                 "Tundra Esports", "AVULUS", "Team Spirit", "Nigma Galaxy",
                                                 "Team Tidebound", "Talon Esports", "Shopify Rebellion", "HEROIC")
        esl_one_ral_2025_invited_teams: Root = Root("esl_one_ral_2025_root", 12, metadata, participating_teams)
        esl_one_ral_2025_invited_teams.bind_forward(esl_one_ral_2025_gs)
        esl_one_ral_2025_gs.set_participating_teams(participating_teams)

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

        esl_one_ral_2025_invited_teams.build()
        esl_one_ral_2025_gs.build()
        esl_one_ral_2025_playoff.build()
        esl_one_ral_2025.build()
        ept_esl_one_ral_2025_gs.build()
        ept_esl_one_ral_2025.build()

        return ept_esl_one_ral_2025, ept_esl_one_ral_2025_gs

