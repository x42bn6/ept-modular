from typing import Tuple

from ept import EptPairGroupStage, EptTournament, SolvedEptStage, SolvedEptTournament, EptStageBase, EptTournamentBase
from metadata import Metadata
from stage import PairGroupStage, DoubleElimination_4U4L2DSL1D, Tournament
from teams import TeamDatabase


class EslOneBangkok2024:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self.team_database = metadata.team_database

    def build(self) -> Tuple[EptTournamentBase, EptStageBase]:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database

        esl_one_bkk_2024_gs: PairGroupStage = PairGroupStage("esl_one_bkk_2024_gs", 6, 4, metadata)
        esl_one_bkk_2024_playoff: DoubleElimination_4U4L2DSL1D = DoubleElimination_4U4L2DSL1D(
            "esl_one_bkk_2024_playoff", metadata, previous_stage_lbr1_1_positions=[6, 7])
        esl_one_bkk_2024: Tournament = Tournament("esl_one_bkk_2024", esl_one_bkk_2024_gs, metadata)

        esl_one_bkk_2024_gs.group_a = team_database.get_teams_by_names("Team Falcons", "AVULUS", "Team Spirit",
                                                                       "Shopify Rebellion", "BOOM Esports",
                                                                       "Natus Vincere")
        esl_one_bkk_2024_gs.group_b = team_database.get_teams_by_names("PARIVISION", "BetBoom Team",
                                                                       "Nigma Galaxy", "Team Liquid", "Gaozu",
                                                                       "M80")

        esl_one_bkk_2024_playoff.bind_backward(esl_one_bkk_2024_gs)
        esl_one_bkk_2024_gs.bind_forward(esl_one_bkk_2024_playoff)

        ept_esl_one_bkk_2024_gs = EptPairGroupStage(esl_one_bkk_2024_gs, [480])
        ept_esl_one_bkk_2024 = EptTournament(esl_one_bkk_2024, ept_esl_one_bkk_2024_gs,
                                             [4800, 3600, 3000, 2400, 1680, 1680, 780, 780, 420, 420, 210, 210],
                                             "ESL One Bangkok 2024",
                                             "ESL One/Bangkok/2024",
                                             "/esl_one",
                                             "2024-12-15",
                                             metadata)

        esl_one_bkk_2024_gs.team_can_finish_between("Team Falcons", 1, 2)
        esl_one_bkk_2024_gs.team_can_finish_between("AVULUS", 3, 4)
        esl_one_bkk_2024_gs.team_can_finish_between("Team Spirit", 5, 6)
        esl_one_bkk_2024_gs.team_can_finish_between("Shopify Rebellion", 7, 8)
        esl_one_bkk_2024_gs.team_can_finish_between("BOOM Esports", 9, 10)
        esl_one_bkk_2024_gs.team_can_finish_between("Natus Vincere", 11, 12)

        esl_one_bkk_2024_gs.team_can_finish_between("PARIVISION", 1, 2)
        esl_one_bkk_2024_gs.team_can_finish_between("BetBoom Team", 3, 4)
        esl_one_bkk_2024_gs.team_can_finish_between("Nigma Galaxy", 5, 6)
        esl_one_bkk_2024_gs.team_can_finish_between("Team Liquid", 7, 8)
        esl_one_bkk_2024_gs.team_can_finish_between("Gaozu", 9, 10)
        esl_one_bkk_2024_gs.team_can_finish_between("M80", 11, 12)

        esl_one_bkk_2024_playoff.ubsf_1.set_winner("BetBoom Team")
        esl_one_bkk_2024_playoff.ubsf_2.set_winner("PARIVISION")
        esl_one_bkk_2024_playoff.ubf.set_winner("PARIVISION")
        esl_one_bkk_2024_playoff.lbr1_1.set_winner("Team Liquid")
        esl_one_bkk_2024_playoff.lbr1_2.set_winner("Team Spirit")
        esl_one_bkk_2024_playoff.lbqf_1.set_winner("Team Liquid")
        esl_one_bkk_2024_playoff.lbqf_2.set_winner("Team Spirit")
        esl_one_bkk_2024_playoff.lbsf.set_winner("Team Liquid")
        esl_one_bkk_2024_playoff.lbf.set_winner("Team Liquid")
        esl_one_bkk_2024_playoff.gf.set_winner("PARIVISION")

        esl_one_bkk_2024_gs.build()
        esl_one_bkk_2024_playoff.build()
        esl_one_bkk_2024.build()
        ept_esl_one_bkk_2024_gs.build()
        ept_esl_one_bkk_2024.build()

        return ept_esl_one_bkk_2024, ept_esl_one_bkk_2024_gs


class EslOneBangkok2024Solved:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata

    def build(self) -> Tuple[EptTournamentBase, EptStageBase]:
        metadata: Metadata = self.metadata

        esl_one_bkk_2024_gs: SolvedEptStage = SolvedEptStage("esl_one_bkk_2024_gs", 12, [480, 480], metadata)
        esl_one_bkk_2024: SolvedEptTournament = SolvedEptTournament("esl_one_bkk_2024", esl_one_bkk_2024_gs,
                                                                    [4800, 3600, 3000, 2400, 1680, 1680, 780, 780, 420,
                                                                     420, 210, 210],
                                                                    "ESL One Bangkok 2024",
                                                                    "ESL One/Bangkok/2024",
                                                                    "/esl_one",
                                                                    "2024-12-15",
                                                                    metadata)

        esl_one_bkk_2024_gs.set_position("Team Falcons", 1)
        esl_one_bkk_2024_gs.set_position("AVULUS", 3)
        esl_one_bkk_2024_gs.set_position("Team Spirit", 5)
        esl_one_bkk_2024_gs.set_position("Shopify Rebellion", 7)
        esl_one_bkk_2024_gs.set_position("BOOM Esports", 9)
        esl_one_bkk_2024_gs.set_position("Natus Vincere", 11)

        esl_one_bkk_2024_gs.set_position("PARIVISION", 2)
        esl_one_bkk_2024_gs.set_position("BetBoom Team", 4)
        esl_one_bkk_2024_gs.set_position("Nigma Galaxy", 6)
        esl_one_bkk_2024_gs.set_position("Team Liquid", 8)
        esl_one_bkk_2024_gs.set_position("Gaozu", 10)
        esl_one_bkk_2024_gs.set_position("M80", 12)

        esl_one_bkk_2024.set_position("PARIVISION", 1)
        esl_one_bkk_2024.set_position("Team Liquid", 2)
        esl_one_bkk_2024.set_position("BetBoom Team", 3)
        esl_one_bkk_2024.set_position("Team Spirit", 4)
        esl_one_bkk_2024.set_position("Team Falcons", 5)
        esl_one_bkk_2024.set_position("AVULUS", 6)
        esl_one_bkk_2024.set_position("Shopify Rebellion", 7)
        esl_one_bkk_2024.set_position("Nigma Galaxy", 8)
        esl_one_bkk_2024.set_position("BOOM Esports", 9)
        esl_one_bkk_2024.set_position("Gaozu", 10)
        esl_one_bkk_2024.set_position("Natus Vincere", 11)
        esl_one_bkk_2024.set_position("M80", 12)

        return esl_one_bkk_2024, esl_one_bkk_2024_gs
