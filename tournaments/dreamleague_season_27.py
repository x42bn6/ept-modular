from typing import Tuple

from ept import EptStageBase, EptTournamentBase, SolvedEptTournament
from metadata import Metadata


class DreamLeagueSeason27Solved:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata

    def build(self) -> EptTournamentBase:
        metadata: Metadata = self.metadata

        dl_s27: SolvedEptTournament = SolvedEptTournament("dl_s27",
                                                          None,
                                                          # Just use final points to avoid Swiss
                                                          [3400, 3000, 2400, 2000, 1600, 1500, 900, 1000,
                                                           400, 400, 400, 400, 400, 400, 400, 400,
                                                           300, 300, 300, 300, 300,
                                                           200, 200, 200],
                                                          "DreamLeague Season 27",
                                                          "DreamLeague/Season 27",
                                                          "/dreamleague",
                                                          "2025-12-21",
                                                          metadata)

        dl_s27.set_position("Team Yandex", 1)
        dl_s27.set_position("Team Spirit", 2)
        dl_s27.set_position("PARIVISION", 3)
        dl_s27.set_position("Xtreme Gaming", 4)
        dl_s27.set_position("OG", 5)
        dl_s27.set_position("Tundra Esports", 6)
        dl_s27.set_position("Virtus.pro", 7)
        dl_s27.set_position("Team Falcons", 8)
        dl_s27.set_position("BetBoom Team", 9)
        dl_s27.set_position("Team Liquid", 10)
        dl_s27.set_position("Natus Vincere", 11)
        dl_s27.set_position("Runa Team", 12)
        dl_s27.set_position("MOUZ", 13)
        dl_s27.set_position("Nigma Galaxy", 14)
        dl_s27.set_position("Team Tidebound", 15)
        dl_s27.set_position("Pipsqueak+4", 16)
        dl_s27.set_position("Amaru Gaming", 17)
        dl_s27.set_position("Aurora Gaming", 18)
        dl_s27.set_position("Team Nemesis", 19)
        dl_s27.set_position("GamerLegion", 20)
        dl_s27.set_position("HEROIC", 21)
        dl_s27.set_position("Passion UA", 22)
        dl_s27.set_position("1w Team", 23)
        dl_s27.set_position("Yakult Brothers", 24)

        return dl_s27
