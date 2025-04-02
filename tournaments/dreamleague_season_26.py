from typing import Tuple

from ept import EptPairGroupStage, EptGroupStage, EptTournament, EptTournamentBase, EptStageBase
from metadata import Metadata
from stage import PairGroupStage, GroupStage, DoubleElimination_2U2L1D, Tournament, RootUnknownAdvances, Root, \
    DoubleElimination_8_2Q_U_4L2DS_1Q
from teams import TeamDatabase, Team


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
        qualified_teams: [Team] = team_database.get_teams_by_names("BOOM Esports",
                                                                   "Tundra Esports", "Gaimin Gladiators")
        declined_teams: [Team] = team_database.get_teams_by_names("Team Spirit")
        dl_s26_invited_teams: Root = Root("dl_s26_root", 12, metadata, participating_teams + qualified_teams)
        dl_s26_invited_teams.bind_forward(dl_s26_gs1)

        na_qualifier: RootUnknownAdvances = RootUnknownAdvances(f"dl_s26_na_qualifier",
                                                                team_database.get_teams_by_names("Shopify Rebellion",
                                                                                                 "NA team 1"),
                                                                1, 1,
                                                                metadata)
        sa_qualifier: RootUnknownAdvances = RootUnknownAdvances(f"dl_s26_sa_qualifier",
                                                                team_database.get_teams_by_names("HEROIC",
                                                                                                 "Perrito Panzon",
                                                                                                 "SA team 1",
                                                                                                 "SA team 2"),
                                                                2, 2,
                                                                metadata)
        weu_qualifier: DoubleElimination_8_2Q_U_4L2DS_1Q = DoubleElimination_8_2Q_U_4L2DS_1Q(f"dl_s26_weu_qualifier",
                                                                                             team_database.get_teams_by_names(
                                                                                                 "Tundra Esports",
                                                                                                 "Team Secret",
                                                                                                 "NAVI Junior",
                                                                                                 "Passion UA",
                                                                                                 "Gaimin Gladiators",
                                                                                                 "Zero Tenacity",
                                                                                                 "AVULUS",
                                                                                                 "Capy Baras"),
                                                                                             metadata)
        eeu_qualifier: RootUnknownAdvances = RootUnknownAdvances(f"dl_s26_eeu_qualifier",
                                                                 team_database.get_teams_by_names("Natus Vincere",
                                                                                                  "EEU team 1"),
                                                                 1, 1,
                                                                 metadata)
        meswa_qualifier: RootUnknownAdvances = RootUnknownAdvances(f"dl_s26_meswa_qualifier",
                                                                   team_database.get_teams_by_names("Virtus.pro",
                                                                                                    "Nigma Galaxy",
                                                                                                    "MESWA team 1"),
                                                                   1, 1,
                                                                   metadata)
        sea_qualifier: RootUnknownAdvances = RootUnknownAdvances(f"dl_s26_sea_qualifier",
                                                                 team_database.get_teams_by_names("Talon Esports",
                                                                                                  "BOOM Esports",
                                                                                                  "SEA team 1",
                                                                                                  "SEA team 2"),
                                                                 2, 2,
                                                                 metadata)
        cn_qualifier: RootUnknownAdvances = RootUnknownAdvances(f"dl_s26_cn_qualifier",
                                                                team_database.get_teams_by_names("Yakult Brothers",
                                                                                                 "Team Tidebound",
                                                                                                 "ex-Xtreme Gaming",
                                                                                                 "Xtreme Gaming",
                                                                                                 "CN team 1",
                                                                                                 "CN team 2"),
                                                                2, 2,
                                                                metadata)

        na_qualifier.bind_forward(dl_s26_gs1)
        sa_qualifier.bind_forward(dl_s26_gs1)
        weu_qualifier.bind_forward(dl_s26_gs1)
        eeu_qualifier.bind_forward(dl_s26_gs1)
        meswa_qualifier.bind_forward(dl_s26_gs1)
        sea_qualifier.bind_forward(dl_s26_gs1)
        cn_qualifier.bind_forward(dl_s26_gs1)

        weu_qualifier.ubr1_1.set_winner("Tundra Esports")
        weu_qualifier.ubr1_2.set_winner("NAVI Junior")
        weu_qualifier.ubr1_3.set_winner("Gaimin Gladiators")
        weu_qualifier.ubr1_4.set_winner("Capy Baras")
        weu_qualifier.ubr2_1.set_winner("Tundra Esports")
        weu_qualifier.ubr2_2.set_winner("Gaimin Gladiators")
        weu_qualifier.lbr1_1.set_winner("Team Secret")
        weu_qualifier.lbr1_2.set_winner("AVULUS")

        na_qualifier.build()
        sa_qualifier.build()
        weu_qualifier.build()
        eeu_qualifier.build()
        meswa_qualifier.build()
        sea_qualifier.build()
        cn_qualifier.build()

        for team in [team for team in team_database.get_all_teams() if
                     team in declined_teams or
                     not team.is_alive]:
            dl_s26.team_declined_or_cannot_participate(team)

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

        dl_s26_invited_teams.build()
        dl_s26_gs1.build()
        dl_s26_gs2.build()
        dl_s26_playoff.build()
        dl_s26.build()
        ept_dl_s26_gs1.build()
        ept_dl_s26_gs2.build()
        ept_dl_s26.build()

        return ept_dl_s26, ept_dl_s26_gs1, ept_dl_s26_gs2
