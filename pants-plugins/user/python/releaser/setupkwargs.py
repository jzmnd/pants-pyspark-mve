"""Rule to create custom kwargs for `python_artifact()` for use in setup.py"""
from __future__ import annotations

import os

from pants.backend.python.util_rules.package_dists import SetupKwargs, SetupKwargsRequest
from pants.engine.fs import DigestContents, GlobMatchErrorBehavior, PathGlobs
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.target import Target
from pants.engine.unions import UnionRule

from user.python.releaser.gitversion import GitVersion


DEFAULT_KWARGS = {
    "author": "Jez Smith",
    "readme": "README.md",
    "url": "https://github.com/jzmnd/pants-pyspark-mve",
}


class CustomSetupKwargsRequest(SetupKwargsRequest):
    @classmethod
    def is_applicable(cls, _: Target) -> bool:
        """Always use our custom `setup()` kwargs generator for `python_distribution` targets."""
        return True


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

    git_version = await Get(GitVersion)
    kwargs["version"] = f"{git_version.tag}.post{git_version.distance}+{git_version.shorthash}"

    kwargs.update(DEFAULT_KWARGS)

    return SetupKwargs(kwargs, address=request.target.address)


def rules():
    return (
        *collect_rules(),
        UnionRule(SetupKwargsRequest, CustomSetupKwargsRequest),
    )
