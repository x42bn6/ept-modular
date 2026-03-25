from typing import Tuple

from ept import EptStageBase, EptTournamentBase, SolvedEptStage, \
    SolvedEptTournament
from metadata import Metadata


class DreamLeagueSeason28Solved:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata

    def build(self) -> Tuple[EptTournamentBase, EptStageBase, EptStageBase]:
        metadata: Metadata = self.metadata

        dl_s28_gs1: SolvedEptStage = SolvedEptStage("dl_s28_gs1", 16, [420, 420, 210, 210, 105, 105], metadata)
        dl_s28_gs2: SolvedEptStage = SolvedEptStage("dl_s28_gs2", 8, [420], metadata)
        dl_s28_gs1.bind_next_ept_stage(dl_s28_gs2)
        dl_s28: SolvedEptTournament = SolvedEptTournament("dl_s28",
                                                          dl_s28_gs1,
                                                          [4800, 4000, 3200, 2560, 1920, 1600, 960, 640, 400, 400, 200,
                                                           200, 112, 112, 48, 48],
                                                          "DreamLeague Season 28",
                                                          "DreamLeague/Season 28",
                                                          "/dreamleague",
                                                          "2026-03-01",
                                                          metadata)

        dl_s28_gs1.set_position("Aurora Gaming", 1)
        dl_s28_gs1.set_position("PARIVISION", 3)
        dl_s28_gs1.set_position("Team Liquid", 5)
        dl_s28_gs1.set_position("BetBoom Team", 7)
        dl_s28_gs1.set_position("OG", 9)
        dl_s28_gs1.set_position("Team Yandex", 11)
        dl_s28_gs1.set_position("paiN Gaming", 13)
        dl_s28_gs1.set_position("Yakult Brothers", 15)

        dl_s28_gs1.set_position("MOUZ", 1)
        dl_s28_gs1.set_position("Tundra Esports", 3)
        dl_s28_gs1.set_position("Team Falcons", 5)
        dl_s28_gs1.set_position("Xtreme Gaming", 7)
        dl_s28_gs1.set_position("Natus Vincere", 9)
        dl_s28_gs1.set_position("Team Spirit", 11)
        dl_s28_gs1.set_position("GamerLegion", 13)
        dl_s28_gs1.set_position("Execration", 15)

        dl_s28_gs2.set_position("Team Liquid", 1)
        dl_s28_gs2.set_position("Tundra Esports", 2)
        dl_s28_gs2.set_position("Aurora Gaming", 3)
        dl_s28_gs2.set_position("Xtreme Gaming", 4)
        dl_s28_gs2.set_position("Team Falcons", 5)
        dl_s28_gs2.set_position("PARIVISION", 6)
        dl_s28_gs2.set_position("BetBoom Team", 7)
        dl_s28_gs2.set_position("MOUZ", 8)

        dl_s28.set_position("Tundra Esports", 1)
        dl_s28.set_position("Aurora Gaming", 2)
        dl_s28.set_position("Team Liquid", 3)
        dl_s28.set_position("Xtreme Gaming", 4)
        dl_s28.set_position("Team Falcons", 5)
        dl_s28.set_position("PARIVISION", 6)
        dl_s28.set_position("BetBoom Team", 7)
        dl_s28.set_position("MOUZ", 8)
        dl_s28.set_position("OG", 9)
        dl_s28.set_position("Natus Vincere", 10)
        dl_s28.set_position("Team Yandex", 11)
        dl_s28.set_position("Team Spirit", 12)
        dl_s28.set_position("paiN Gaming", 13)
        dl_s28.set_position("GamerLegion", 14)
        dl_s28.set_position("Yakult Brothers", 15)
        dl_s28.set_position("Execration", 16)

        return dl_s28, dl_s28_gs1, dl_s28_gs2
