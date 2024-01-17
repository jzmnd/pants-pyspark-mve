"""Plugin to create custom kwargs for `python_artifact()` for use in setup.py"""
from __future__ import annotations

import os
import re

from pants.backend.python.util_rules.package_dists import SetupKwargs, SetupKwargsRequest
from pants.base.build_root import BuildRoot
from pants.core.util_rules.system_binaries import BinaryPathRequest, BinaryPaths
from pants.engine.fs import DigestContents, GlobMatchErrorBehavior, PathGlobs
from pants.engine.process import Process, ProcessCacheScope, ProcessResult
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.target import Target
from pants.engine.unions import UnionRule


DEFAULT_KWARGS = {
    "author": "Jez Smith",
    "readme": "README.md",
    "url": "https://github.com/jzmnd/pants-pyspark-mve"
}


class CustomSetupKwargsRequest(SetupKwargsRequest):
    @classmethod
    def is_applicable(cls, _: Target) -> bool:
        """Always use our custom `setup()` kwargs generator for `python_distribution` targets."""
        return True


class GitTagVersion(str):
    pass


@rule
async def get_git_repo_version(build_root: BuildRoot) -> GitTagVersion:
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
    return GitTagVersion(git_describe.stdout.decode().strip())


@rule
async def setup_kwargs_plugin(request: CustomSetupKwargsRequest) -> SetupKwargs:
    kwargs = request.explicit_kwargs.copy()

    if "name" not in kwargs:
        raise ValueError(
            f"Missing a `name` kwarg in the `provides` field for {request.target.address}."
        )
    if "description" not in kwargs:
        raise ValueError(
            f"Missing a `description` kwarg in the `provides` field for {request.target.address}."
        )

    build_file_path = request.target.address.spec_path
    long_description_path = os.path.join(build_file_path, "README.md")
    digest_contents = await Get(
        DigestContents,
        PathGlobs(
            [long_description_path],
            description_of_origin="the project README.md file",
            glob_match_error_behavior=GlobMatchErrorBehavior.error,
        ),
    )
    kwargs["long_description"] = digest_contents[0].content.decode()

    git_repo_version = await Get(GitTagVersion)
    git_repo_version_match = re.search(r"^(.+)-(\d+)-g([0-9a-f]+)$", git_repo_version)
    tag = git_repo_version_match.group(1)
    distance = git_repo_version_match.group(2)
    shorthash = git_repo_version_match.group(3)
    kwargs["version"] = f"{tag}.post{distance}+{shorthash}"

    kwargs.update(DEFAULT_KWARGS)

    return SetupKwargs(kwargs, address=request.target.address)


def rules():
    return (
        *collect_rules(),
        UnionRule(SetupKwargsRequest, CustomSetupKwargsRequest),
    )
