from typing import Tuple

from constants import MAX_TEAMS_PER_REGION
from ept import EptPairGroupStage, EptGroupStage, EptTournament, EptTournamentBase, EptStageBase
from metadata import Metadata
from stage import PairGroupStage, GroupStage, DoubleElimination_2U2L1D, Tournament, RootUnknownAdvances, Root
from teams import TeamDatabase, Team, Region


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

        participating_teams: [Team] = team_database.get_teams_by_names("PARIVISION", "BetBoom Team", "Team Falcons",
                                                                       "Team Spirit")
        dl_s26_invited_teams: Root = Root("dl_s26_root", 12, metadata, participating_teams)
        dl_s26_invited_teams.bind_forward(dl_s26_gs1)

        regional_qualifiers: [RootUnknownAdvances] = []
        for region in Region:
            regional_qualifier_teams = [team for team in (team_database.get_teams_by_region(region))
                                        if team not in participating_teams and team.is_alive]
            regional_qualifier: RootUnknownAdvances = RootUnknownAdvances(f"dl_s26_{region}_qualifier",
                                                                          regional_qualifier_teams, 1, MAX_TEAMS_PER_REGION, metadata)
            regional_qualifier.bind_forward(dl_s26_gs1)
            regional_qualifiers.append(regional_qualifier)

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

        for regional_qualifier in regional_qualifiers:
            regional_qualifier.build()

        dl_s26_invited_teams.build()
        dl_s26_gs1.build()
        dl_s26_gs2.build()
        dl_s26_playoff.build()
        dl_s26.build()
        ept_dl_s26_gs1.build()
        ept_dl_s26_gs2.build()
        ept_dl_s26.build()

        return ept_dl_s26, ept_dl_s26_gs1, ept_dl_s26_gs2
