# Devtools

This folder provides conda environment definitions and a conda-build recipe.

## Create conda environment

Development:

```bash
conda env create -f devtools/conda-envs/development_env.yaml -n smonitor-dev
```

## Build the conda package locally

Use the development environment or a dedicated build env if needed.
The `meta.yaml` uses `GIT_DESCRIBE_TAG` for the version. Ensure your git tags are set or
export the variable before building.
