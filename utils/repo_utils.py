import git
import sys
from dataclasses import dataclass
from pathlib import Path


WORK_DIR = Path("/tmp/ovn-website-workdir")


@dataclass
class OVNBranch:
    year: int
    month: int
    full_year: int

    def __init__(self, branch: str):
        year_s, _, month_s = branch.partition(".")
        self.year = int(year_s)
        self.month = int(month_s)
        self.full_year = self.year + 2000

    def __str__(self):
        return f"{self.year}.{self.month:02}"

    def __lt__(self, branch):
        return str(self) < str(branch)

    def full_branch(self) -> str:
        return f"branch-{self}"


def setup_repo(path: Path, url: str) -> git.Repo:
    if not WORK_DIR.exists():
        WORK_DIR.mkdir()

    if not path.exists():
        path.mkdir()

    repo = git.Repo.init(path)
    if "origin" not in repo.remotes:
        origin = repo.create_remote("origin", url)
    else:
        origin = repo.remotes["origin"]

    origin.fetch()
    return repo


def checkout_branch(repo: git.Repo, branch: str, remote_name: str = "origin"):
    remote = repo.remotes[remote_name]
    if branch not in remote.refs:
        print(f"Branch {branch} not found")
        sys.exit(1)

    new_branch = repo.create_head(branch, remote.refs[branch])
    new_branch.set_tracking_branch(remote.refs[branch])
    new_branch.checkout()
