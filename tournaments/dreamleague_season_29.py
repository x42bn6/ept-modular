from typing import Tuple, Dict

from ortools.sat.python.cp_model import IntVar, CpModel

from ept import EptPairGroupStage, EptGroupStage, EptTournament, EptTournamentBase, EptStageBase
from metadata import Metadata
from stage import PairGroupStage, GroupStage, DoubleElimination_2U2L1D, Tournament
from teams import TeamDatabase, Team, Region


class DreamLeagueSeason29:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self.team_database = metadata.team_database

    def build(self) -> Tuple[EptTournamentBase, EptStageBase, EptStageBase]:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database
        model: CpModel = metadata.model

        dl_s29_gs1: PairGroupStage = PairGroupStage("dl_s29_gs1", 8, 4, metadata)
        dl_s29_gs2: GroupStage = GroupStage("dl_s29_gs2", 8, 4, metadata)
        dl_s29_playoff: DoubleElimination_2U2L1D = DoubleElimination_2U2L1D("dl_s29_playoff", metadata)
        dl_s29: Tournament = Tournament("dl_s29", dl_s29_gs1, metadata)

        # 6 of the top 8 of ESL One Birmingham 2026 will be in the top 6 at the end of the event
        guaranteed_invites: [Team] = team_database.get_teams_by_names("Tundra Esports", "Team Yandex", "Xtreme Gaming", "Aurora Gaming", "PARIVISION", "Team Spirit")
        for g in guaranteed_invites:
            team_index: int = team_database.get_team_index(g)
            model.Add(sum(dl_s29_gs1.indicators[team_index]) == 1)

        region_slots: Dict[Region, int] = {
            Region.WEU: 3,
            Region.EEU: 1,
            Region.CN: 1,
            Region.SA: 1,
            Region.SEA: 1,
            Region.NA: 1
        }
        for region, slots in region_slots.items():
            team_sum: IntVar = 0
            for t in team_database.get_teams_by_region(region):
                if t in guaranteed_invites:
                    continue
                team_index: int = team_database.get_team_index(t)
                team_sum += sum(dl_s29_gs1.indicators[team_index])
            model.Add(team_sum >= slots)

        dl_s29_gs1.bind_forward(dl_s29_gs2)
        dl_s29_playoff.bind_backward(dl_s29_gs2)
        dl_s29_gs2.bind_forward(dl_s29_playoff)
        ept_dl_s29_gs1 = EptPairGroupStage(dl_s29_gs1, [600, 300, 150])
        ept_dl_s29_gs2 = EptGroupStage(dl_s29_gs2, [600])
        ept_dl_s29_gs1.bind_next_ept_stage(ept_dl_s29_gs2)

        ept_dl_s29 = EptTournament(dl_s29,
                                   ept_dl_s29_gs1,
                                   [6000, 5000, 4000, 3200, 2400, 2000, 1200, 800, 500, 500, 250, 250, 140, 140, 60,
                                    60],
                                   "DreamLeague Season 29",
                                   "DreamLeague/Season 29",
                                   "/dreamleague",
                                   "2026-05-24",
                                   metadata)

        dl_s29_gs1.build()
        dl_s29_gs2.build()
        dl_s29_playoff.build()
        dl_s29.build()
        ept_dl_s29_gs1.build()
        ept_dl_s29_gs2.build()
        ept_dl_s29.build()

        return ept_dl_s29, ept_dl_s29_gs1, ept_dl_s29_gs2
