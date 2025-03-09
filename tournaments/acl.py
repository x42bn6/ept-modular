from ept import EptTournament, EptTournamentBase, EptGroupStage
from metadata import Metadata
from stage import Tournament, GroupStage, Root
from teams import TeamDatabase, Team, Region


class AsianChampionsLeague:
    def __init__(self, metadata: Metadata):
        self.metadata = metadata
        self.team_database = metadata.team_database

    def build(self) -> EptTournamentBase:
        metadata: Metadata = self.metadata
        team_database: TeamDatabase = self.team_database

        chinese_teams: [Team] = team_database.get_teams_by_region(Region.CN)

        chinese_teams_root: Root = Root("acl_root", len(chinese_teams), metadata, chinese_teams)
        acl_gs: GroupStage = GroupStage("acl_gs", len(chinese_teams), 1, metadata)
        acl = Tournament("acl", acl_gs, metadata)
        ept_acl_gs: EptGroupStage = EptGroupStage(acl_gs, [])
        ept_acl = EptTournament(acl, ept_acl_gs,
                                [20000],
                                "Asian Champions League 2025",
                                "Hero_Esports/Asian_Champions_League/2025",
                                "Hero Esports Asian Champions League icon allmode.png",
                                "2025-05-16",
                                metadata)
        acl_gs.set_participating_teams(chinese_teams)

        chinese_teams_root.bind_forward(acl_gs)

        chinese_teams_root.build()
        acl_gs.build()
        acl.build()
        ept_acl_gs.build()
        ept_acl.build()

        return ept_acl
