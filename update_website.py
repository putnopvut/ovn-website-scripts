#!/usr/bin/env python3

import git
import utils.changelog as changelog
import datetime
import utils.repo_utils as repo_utils
from argparse import ArgumentParser
from typing import List, Tuple, Dict
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

OVN_URL = "https://github.com/ovn-org/ovn"
OVN_DIR = repo_utils.WORK_DIR / "ovn"
WEBSITE_URL = "https://github.com/ovn-org/ovn-website"
WEBSITE_DIR = repo_utils.WORK_DIR / "ovn-website"
RELEASE_DIR = WEBSITE_DIR / "src/content/releases"

SUPPORTED_BRANCHES = Path("supported_branches.txt")
UNSUPPORTED_BRANCHES = Path("unsupported_branches.txt")


def is_branch_lts(branch: repo_utils.OVNBranch) -> bool:
    return branch.year % 2 == 0 and branch.month == 3


def get_support_dates(
    release_date: datetime.date, is_lts: bool
) -> Tuple[datetime.date, datetime.date]:
    if is_lts:
        crit_date = release_date.replace(year=release_date.year + 2)
        end_date = release_date.replace(year=release_date.year + 3)
    else:
        end_date = release_date.replace(year=release_date.year + 1)
        crit_date = end_date

    return crit_date, end_date


def get_branch_list(branch_file: Path):
    if not branch_file.exists():
        return []

    with open(branch_file, "r") as bf:
        return [repo_utils.OVNBranch(branch.strip()) for branch in bf]


def get_news(news_file: Path, branch_tags: List[str]) -> Dict[str, str]:
    # There is no standard formatting used in NEWS. Trying to parse individual
    # items is a bad idea. Instead, we return the news for a particular release
    # as a big multi-line string.
    news_dict = defaultdict(str)
    with open(news_file, "r") as news:
        for line in news:
            # When we reach a line starting with "v", then we have reached the
            # point before OVN separated from OVS and can stop.
            if line.startswith("v"):
                break
            if line.startswith("OVN v"):
                cur_tag = line[4:12]
            if cur_tag and cur_tag in branch_tags:
                news_dict[cur_tag] += line

    return news_dict


def write_release(
    website_repo: git.Repo,
    branch: repo_utils.OVNBranch,
    today: datetime.date,
    release_date: datetime.date,
    crit_date: datetime.date,
    end_date: datetime.date,
    is_lts: bool,
    changelogs: List[changelog.Changelog],
    news: Dict[str, str],
    env: Environment,
):
    template = env.get_template("new_release_template.md")

    releases = []
    for log in reversed(changelogs):
        release_date = datetime.datetime.fromtimestamp(
            log.end_tag.commit.committed_date
        )
        releases.append(
            {
                "tag": log.end_tag.tag,
                "url": f"{OVN_URL}/releases/tag/{log.end_tag.tag}",
                "news": news[log.end_tag.tag],
                "changelog_path": f"../changelog_{log.end_tag.tag}",
                "release_date": release_date,
            }
        )

    release_path = RELEASE_DIR / f"{branch}.md"

    context = {
        "branch": branch,
        "today": today,
        "crit_date": crit_date,
        "end_date": end_date,
        "release_date": release_date,
        "releases": releases,
        "is_lts": is_lts,
        "weight": 99999999999 - release_date.timestamp(),
    }

    with open(release_path, "w") as release_file:
        release_file.write(template.render(context))


def write_changelogs(
    website_repo: git.Repo,
    changelogs: List[changelog.Changelog],
    env: Environment,
):
    template = env.get_template("changelog_template.md")
    for log in changelogs:
        context = {
            "start_tag": log.start_tag.tag,
            "end_tag": log.end_tag.tag,
            "commits": log.iter_commits(),
            "github_url": OVN_URL,
        }
        changelog_path = RELEASE_DIR / f"changelog_{log.end_tag.tag}.md"
        with open(changelog_path, "w") as cl_file:
            cl_file.write(template.render(context))


def write_all_releases(
    website_repo: git.Repo,
    supported_branches: List[str],
    unsupported_branches: List[str],
    env: Environment,
):
    template = env.get_template("all_releases.md")
    context = {
        "supported_branches": supported_branches,
        "unsupported_branches": unsupported_branches,
    }
    all_releases_path = RELEASE_DIR / "all_releases.md"
    with open(all_releases_path, "w") as or_file:
        or_file.write(template.render(context))


def write_branch_list(branch_file: Path, branches):
    with open(branch_file, "w") as bf:
        for branch in branches:
            bf.write(f"{branch}\n")


def write_release_index(
    website_repo: git.Repo,
    supported_branches: List[repo_utils.OVNBranch],
    env: Environment,
):
    most_recent_lts = None
    for branch in reversed(supported_branches):
        if is_branch_lts(branch):
            most_recent_lts = branch
            break

    template = env.get_template("release_index.md")
    context = {
        "most_recent": supported_branches[-1],
        "most_recent_lts": most_recent_lts,
    }
    release_index_path = RELEASE_DIR / "_index.en.md"
    with open(release_index_path, "w") as index_file:
        index_file.write(template.render(context))


def main():
    parser = ArgumentParser(description="New release")
    parser.add_argument("branch", help="OVN branch")
    args = parser.parse_args()

    ovn_repo = repo_utils.setup_repo(OVN_DIR, OVN_URL)
    website_repo = repo_utils.setup_repo(WEBSITE_DIR, WEBSITE_URL)

    branch = repo_utils.OVNBranch(args.branch)

    repo_utils.checkout_branch(ovn_repo, branch.full_branch())
    repo_utils.checkout_branch(website_repo, "main")
    changelogs = changelog.get_changelogs(ovn_repo, branch)

    release_date = datetime.date.fromtimestamp(
        changelogs[0].end_tag.commit.committed_date
    )
    is_lts = is_branch_lts(branch)
    today = datetime.date.today()
    crit_date, end_date = get_support_dates(release_date, is_lts)

    branch_tags = [log.end_tag.tag for log in changelogs]
    news = get_news(OVN_DIR / "NEWS", branch_tags)

    supported_branches = get_branch_list(SUPPORTED_BRANCHES)
    unsupported_branches = get_branch_list(UNSUPPORTED_BRANCHES)

    if today < end_date:
        if branch not in supported_branches:
            supported_branches.append(branch)
    else:
        if branch in supported_branches:
            supported_branches.remove(branch)
        if branch not in unsupported_branches:
            unsupported_branches.append(branch)

    supported_branches.sort()
    unsupported_branches.sort()

    env = Environment(loader=FileSystemLoader("templates/"))
    write_release(
        website_repo,
        branch,
        today,
        release_date,
        crit_date,
        end_date,
        is_lts,
        changelogs,
        news,
        env,
    )
    write_changelogs(website_repo, changelogs, env)

    write_all_releases(
        website_repo,
        reversed(supported_branches),
        reversed(unsupported_branches),
        env,
    )
    write_release_index(website_repo, supported_branches, env)

    write_branch_list(SUPPORTED_BRANCHES, supported_branches)
    write_branch_list(UNSUPPORTED_BRANCHES, unsupported_branches)


if __name__ == "__main__":
    main()
