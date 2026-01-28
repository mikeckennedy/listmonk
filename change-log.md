# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.3.10] - 2026-01-28

### Added
* Add update_list function (thanks @ChrisH861, PR #27)

## [0.3.9] - 2026-01-05

### Added
* Add add_subscribers_to_lists function (thanks @MochaSteve256)

### Changed
* Loosen some of the types to allow more flexible usage (avoid type errors when DTOs/ViewModels/etc have VALUE|None typing but are known to be in a good state)
* Refactor client implementation to improve organization and maintainability

## [0.3.8] - 2025-10-22

### Added
- Support for subject parameter in transactional templates (PR #24)
- FAQ section to README.md (PR #22)
- Four new API methods to the public interface
- CLAUDE.md with project overview, development commands, code style, and key patterns
- WARP.md documentation
- Ruff formatting configuration

### Changed
- Extensive type annotation improvements for better IDE support (PyLance/VS Code)
- HTTP response validation and parsing refactored for better error handling
- Headers type fix: now properly uses string values instead of list of dictionaries
- Code formatting with ruff throughout the codebase
- Documentation improvements in README.md

### Fixed
- Custom exception renamed from `FileNotFoundError` to `ListmonkFileNotFoundError` to avoid builtin conflict
- Non-string to string types in `__all__` exports
- Type inference error in code fragments

[unreleased]: https://github.com/mikeckennedy/listmonk/compare/v0.3.10...HEAD
[0.3.10]: https://github.com/mikeckennedy/listmonk/compare/v0.3.9...v0.3.10
[0.3.9]: https://github.com/mikeckennedy/listmonk/compare/v0.3.8...v0.3.9
[0.3.8]: https://github.com/mikeckennedy/listmonk/releases/tag/v0.3.8

