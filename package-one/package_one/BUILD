resource(
    name="pyproject",
    source="pyproject.toml",
)

python_distribution(
    name="package-one",
    dependencies=[
        ":pyproject",
    ],
    provides=python_artifact(
        name="package-one",
        description="An example PySpark package.",
    ),
)
