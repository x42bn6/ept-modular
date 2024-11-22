class Team:
    def __init__(self, name: str = None):
        self.name = name
        self.ept_relevant = False

    def make_relevant(self):
        self.ept_relevant = True


class TeamDatabase:
    def __init__(self):
        self.teams = {}

    def add_team(self, team: Team):
        self.teams[team.name] = team

    def get_team_by_name(self, team_name: str) -> Team:
        if self.teams.get(team_name) is None:
            raise Exception(f"No such team {team_name}")

        return self.teams[team_name]

    def get_teams_by_names(self, *team_names: str) -> [Team]:
        return list(map(self.get_team_by_name, team_names))

    def get_team_index(self, team: Team) -> int:
        return list(self.teams.keys()).index(team.name)

    def get_team_index_by_team_name(self, team_name: str) -> int:
        return list(self.teams.keys()).index(team_name)

    def get_all_teams(self) -> [Team]:
        return self.teams.values()