# pants-pyspark-mve

## Background
Minimum viable example repo for running [Pants](https://www.pantsbuild.org) with [PySpark](https://spark.apache.org) libraries.
Motivation was to provide a proof of concept for running PySpark unit tests in Pants, particularly when using various UDFs.
Also includes a Pants plugin that uses `git describe` to automatically generate package versions in the `python_distribution` target.

## How to
To run tests with PySpark, `JAVA_HOME` must be set before running any Pants commands.

MacOS example with openjdk 11 installed via [homebrew](https://brew.sh):
```bash
export JAVA_HOME=/opt/homebrew/Cellar/openjdk@11/11.0.21/libexec/openjdk.jdk/Contents/Home/
pants lint ::
pants check ::
pants test ::
pants package ::
```
