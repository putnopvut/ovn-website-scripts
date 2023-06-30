#!/usr/bin/env python3

import git
import itertools
from dataclasses import dataclass
from typing import List
from utils.repo_utils import OVNBranch


@dataclass
class TaggedCommit:
    tag: str
    commit: git.Commit


@dataclass
class Changelog:
    repo: git.Repo
    start_tag: TaggedCommit
    end_tag: TaggedCommit

    def iter_commits(self):
        start_commit = self.start_tag.commit.hexsha
        end_commit = self.end_tag.commit.hexsha
        return self.repo.iter_commits(
            f"{start_commit}..{end_commit}", no_merges=True
        )


def get_branch_genesis(repo: git.Repo, branch: OVNBranch) -> TaggedCommit:
    if branch.year == 20 and branch.month == 3:
        # branch-20.03 is a special case because it's the first OVN version
        # that was made after splitting from OVS. Therefore, the previous
        # branch does not follow the same pattern. The previous major release
        # is "2.12.0".
        previous = "2.12.0"
    elif branch.year >= 24:
        if branch.month == 3:
            previous = f"{branch.year-1}.09.0"
        else:
            previous = f"{branch.year}.03.0"
    else:
        if branch.month == 3:
            previous = f"{branch.year-1}.12.0"
        else:
            previous = f"{branch.year}.{branch.month-3:02}.0"

    commit_description = f"Prepare for post-{previous}"
    for commit in repo.iter_commits():
        if commit.summary.startswith(commit_description):
            return TaggedCommit(previous, commit)

    # This is a failsafe, since there has been at least one time (ovn 21.06.0
    # in particular), where there wasn't a "Prepare for post-{tag}" commit.
    commit_description = f"Prepare for {previous}"
    for commit in repo.iter_commits():
        if commit.summary.startswith(commit_description):
            return TaggedCommit(previous, commit)

    return None


def get_tags(repo: git.Repo, branch: OVNBranch) -> List[TaggedCommit]:
    tags = [get_branch_genesis(repo, branch)]
    candidate_tags = (tag for tag in repo.tags if tag is not None)
    for tag in sorted(candidate_tags, key=lambda x: x.tag.tag):
        tag_num = tag.tag.tag[1:6]
        if tag_num == str(branch):
            tags.append(TaggedCommit(tag.tag.tag, tag.commit))

    return tags


def get_changelogs(repo: git.Repo, branch: OVNBranch) -> List[Changelog]:
    tags = get_tags(repo, branch)
    tag_pairs = itertools.pairwise(tags)
    return [
        Changelog(repo, start_tag, end_tag) for start_tag, end_tag in tag_pairs
    ]
