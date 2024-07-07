"""Rule to fetch the repo version from the git tag as given by `git describe`"""
from __future__ import annotations

import re
from dataclasses import dataclass

from pants.base.build_root import BuildRoot
from pants.core.util_rules.system_binaries import BinaryPathRequest, BinaryPaths
from pants.engine.process import Process, ProcessCacheScope, ProcessResult
from pants.engine.rules import Get, collect_rules, rule


@dataclass(frozen=True)
class GitVersion:
    tag: str
    distance: str
    shorthash: str


@rule
async def get_git_repo_version(build_root: BuildRoot) -> GitVersion:
    git_paths = await Get(
        BinaryPaths,
        BinaryPathRequest(
            binary_name="git",
            search_path=["/usr/bin", "/bin"],
        ),
    )
    git_bin = git_paths.first_path
    if git_bin is None:
        raise OSError("Could not find 'git'.")
    git_describe = await Get(
        ProcessResult,
        Process(
            argv=[git_bin.path, "-C", build_root.path, "describe", "--tags", "--always", "--long"],
            description="version from `git describe`",
            cache_scope=ProcessCacheScope.PER_SESSION,
        ),
    )
    git_describe = git_describe.stdout.decode().strip()
    git_describe_match = re.search(r"^(.+)-(\d+)-g([0-9a-f]+)$", git_describe)

    return GitVersion(
        tag=git_describe_match.group(1),
        distance=git_describe_match.group(2),
        shorthash=git_describe_match.group(3),
    )


def rules():
    return collect_rules()
