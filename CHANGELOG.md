# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned

- Statement signing (xAPI spec section 4.5)
- Attachment handling

## [0.1.0] - 2026-05-18

### Added

- Async xAPI client built on httpx with configurable timeouts and per-instance headers
- Sync client wrapping the async one for use in non-async codebases
- Pydantic v2 statement models covering the xAPI 1.0.3 spec (Statement, Actor, Verb, Activity, Result, Context)
- Built-in verb registry with the standard ADL verbs; custom verbs supported via direct `Verb(id=...)` construction with full IRIs
- LRS Statement API: send single/batch, get by ID, query with filters, and `get_all_statements()` auto-pagination over xAPI's opaque `more` URLs
- LRS State API: set, get, and delete activity/agent state documents
- Activity Profile API: get and set activity profile documents
- Actor helper builders (`Actor.from_email`, `Actor.from_account`) plus Group support via the `member` field
- ISO 8601 duration utilities (`parse_duration`, `format_duration`)
- Typed exception hierarchy (`LRSAuthError`, `LRSConnectionError`, `LRSResponseError`)
- Python 3.10, 3.11, and 3.12 support (matrix-tested in CI)
