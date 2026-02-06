# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
- Added local bundle export (`smonitor export`) with optional event buffering.
- Hardened file/json handlers (auto-create parent dirs, safer JSON serialization).
- Expanded event schema validation (types + ISO timestamp checks).
- Added docs for bundles and troubleshooting.

## [0.2.0] - 2026-02-06
- Initial public draft with core manager, emitters, handlers, policy engine, and profiling tools.
