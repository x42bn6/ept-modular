from abc import ABC
from typing import Tuple

from pandas.core.interchange.dataframe_protocol import ColumnNullType

from ept import EptPairGroupStage, EptGroupStage, EptTournament, EptTournamentBase, EptStageBase, EptStage
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
                                                                       "Team Liquid")
        qualified_teams: [Team] = team_database.get_teams_by_names("OG.LATAM", "Edge (team)",
                                                                   "Shopify Rebellion",
                                                                   "Gaimin Gladiators", "AVULUS", "NAVI Junior",
                                                                   "Aurora Gaming",
                                                                   "Nigma Galaxy",
                                                                   "BOOM Esports", "Talon Esports",
                                                                   "Xtreme Gaming")
        declined_teams: [Team] = team_database.get_teams_by_names("Team Spirit", "Tundra Esports")
        dl_s26_invited_teams: Root = Root("dl_s26_root", 12, metadata, participating_teams + qualified_teams)
        dl_s26_invited_teams.bind_forward(dl_s26_gs1)

        cn_qualifier: RootUnknownAdvances = RootUnknownAdvances(f"dl_s26_cn_qualifier",
                                                                team_database.get_teams_by_names("Yakult Brothers",
                                                                                                 "CN team 1"),
                                                                1, 1,
                                                                metadata)
        cn_qualifier.bind_forward(dl_s26_gs1)
        cn_qualifier.build()

        for team in [team for team in team_database.get_all_teams() if
                     team in declined_teams]:
            dl_s26.team_declined_or_cannot_participate(team)

        dl_s26_gs1.bind_forward(dl_s26_gs2)
        dl_s26_playoff.bind_backward(dl_s26_gs2)
        dl_s26_gs2.bind_forward(dl_s26_playoff)
        ept_dl_s26_gs1 = EptPairGroupStage(dl_s26_gs1, [600, 300, 150])
        ept_dl_s26_gs2 = EptGroupStage(dl_s26_gs2, [600])
        ept_dl_s26_gs1.bind_next_ept_stage(ept_dl_s26_gs2)

        # Small optimisation - we know which teams will not be competing, but it's not easy to define this in ept.py.
        # If we don't do this, then it will try and predict "dead" teams like Nouns Esports as if they could qualify.
        # We cannot mark teams as "dead" and ignore them, however, as a dead team might finish in the top 10, depending on definition.
        # Notably, as of pre-DL S26, Virtus.pro are in the top-8 but cannot gain more points.
        # Remove once we know DL S26 groups.
        class EptDreamLeagueSeason26(EptTournament, ABC):
            def get_maximum_points_for_team(self, team: Team) -> int:
                if not self.tournament.is_team_participating(team):
                    return 0

                # Only Chinese teams are undetermined; any other region is either invited or qualified
                if not team in participating_teams + qualified_teams and team.region != Region.CN:
                    return 0

                max_points: int = self.points[0]
                next_ept_stage: EptStage = self.first_ept_stage
                while next_ept_stage is not None:
                    max_points += next_ept_stage.points[0]
                    next_ept_stage = next_ept_stage.next_ept_stage

                return max_points

        ept_dl_s26 = EptDreamLeagueSeason26(dl_s26,
                                   ept_dl_s26_gs1,
                                   [6000, 5000, 4000, 3200, 2400, 2000, 1200, 800, 500, 500, 250, 250, 140, 140, 60,
                                    60],
                                   "DreamLeague Season 26",
                                   "DreamLeague/Season 26",
                                   "/dreamleague",
                                   "2025-06-01",
                                   metadata)

        dl_s26_invited_teams.build()
        dl_s26_gs1.build()
        dl_s26_gs2.build()
        dl_s26_playoff.build()
        dl_s26.build()
        ept_dl_s26_gs1.build()
        ept_dl_s26_gs2.build()
        ept_dl_s26.build()

        return ept_dl_s26, ept_dl_s26_gs1, ept_dl_s26_gs2
