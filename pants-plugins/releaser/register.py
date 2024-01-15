""""""
from __future__ import annotations

import os

from pants.backend.python.util_rules.package_dists import SetupKwargs, SetupKwargsRequest
from pants.base.build_root import BuildRoot
from pants.core.util_rules.system_binaries import BinaryPathRequest, BinaryPaths
from pants.engine.fs import DigestContents, GlobMatchErrorBehavior, PathGlobs
from pants.engine.process import Process, ProcessResult
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.target import Target
from pants.engine.unions import UnionRule


class CustomSetupKwargsRequest(SetupKwargsRequest):

    @classmethod
    def is_applicable(cls, _: Target) -> bool:
        """Always use our custom `setup()` kwargs generator for `python_distribution` targets."""
        return True


@rule
async def setup_kwargs_plugin(request: CustomSetupKwargsRequest, build_root: BuildRoot) -> SetupKwargs:
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

    git_paths = await Get(
        BinaryPaths,
        BinaryPathRequest(
            binary_name="git",
            search_path=["/usr/bin", "/bin"],
        ),
    )
    git_bin = git_paths.first_path
    git_describe = await Get(
        ProcessResult,
        Process(
            argv=[
                git_bin.path,
                "-C", build_root.path,
                "describe", "--tags", "--always", "--dirty",
            ],
            description="version from `git describe`",
        )
    )
    git_describe_items = git_describe.stdout.decode().strip().split("-")
    version = f"{git_describe_items[0]}.post{git_describe_items[1]}+{git_describe_items[2]}"

    kwargs["version"] = version

    kwargs["author"] = "Jez Smith"
    kwargs["readme"] = "README.md"
    kwargs["url"] = "https://github.com/jzmnd/pants-pyspark-mve"

    return SetupKwargs(kwargs, address=request.target.address)


def rules():
    return (
        *collect_rules(),
        UnionRule(SetupKwargsRequest, CustomSetupKwargsRequest),
    )
