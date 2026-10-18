from dataclasses import dataclass
import requests

@dataclass
class Repository:
    name: str
    stars:int
    forks:int
    language:str|None

class GitHubClient:
    def get_repositries(self,userName:str)->list[Repository]:
        url: str | None = f"https://api.github.com/users/{userName}/repos"
        repositories:list[Repository] = []
        try:
            while url:
                response = requests.get(url,timeout=10)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data,list):
                    raise  ValueError("Expected list of repositories")
                for item in data:
                    repo = Repository(
                        name=item["full_name"],
                        stars=item["stargazers_count"],
                        forks = item["forks_count"],
                        language = item["language"],
                    )
                    repositories.append(repo)
            return repositories
        except Exception as error:
            print("Error",error)
            return []


class RepositoryAnalytics:
    def __init__(self,repositories:list[Repository]):
        self.repositories:list[Repository] = repositories
    def total_stars(self)->int:
        return sum(repo.star for repo in self.repositories)
    def average_stars(self)->float:
        if not self.repositories:
            return 0
        return self.total_stars()/len(self.repositories)
    def repo_by_language(self)->dict[str,int]:
        counts:dict[str,int] = {}
        for repo in self.repositories:
            language = repo.get("language") or "Unknown"
            counts[language] = counts.get(language,0)+1
        return counts

def main()->None:
    userName = "jpillai"
    client = GitHubClient()
    repositories = client.get_repositries(userName)
    analytics = RepositoryAnalytics(repositories)
    print(f"TotalStar:{analytics.total_stars()}")

if __name__ == "__main__":
    main()
