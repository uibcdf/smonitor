# Devtools

This folder provides conda environment definitions and a conda-build recipe.

## Create conda environments

Development:

```bash
conda env create -f devtools/conda-envs/development_env.yaml -n smonitor-dev
```

Tests:

```bash
conda env create -f devtools/conda-envs/test_env.yaml -n smonitor-test
```

QA:

```bash
conda env create -f devtools/conda-envs/qa_env.yaml -n smonitor-qa
```

Docs:

```bash
conda env create -f devtools/conda-envs/docs_env.yaml -n smonitor-docs
```

Build:

```bash
conda env create -f devtools/conda-envs/build_env.yaml -n smonitor-build
```

## Build the conda package locally

Use the build environment for packaging:
The `meta.yaml` uses `GIT_DESCRIBE_TAG` for the version. Ensure your git tags are set or
export the variable before building.
