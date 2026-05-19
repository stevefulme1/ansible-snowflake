# Changelog

## [2.1.1] - 2026-05-18

### Security
- Mask password in SQL return value from user module to prevent credential leak
- Validate function/procedure body does not contain `$$` delimiter to prevent SQL injection breakout in cortex_function, snowpark_function, and snowpark_procedure modules
- Re-enable S608 (SQL injection) ruff lint rule in CI
- Add .gitignore entries for build artifacts and sensitive files
- Remove tracked .tar.gz build artifact from repository

## [2.0.0] - 2026-05-17

### Added
- Pagination support (limit/offset) for all _info modules
- 4 operational roles: warehouse_setup, database_provision, security_config, data_pipeline
- Dynamic table and Cortex function modules
- Comprehensive unit and integration test suites (14 additional modules)
- Pre-commit and linting configuration (ruff, ansible-lint)

### Fixed
- SQL injection vulnerability fixed via string escaping in all modules
- Warehouse module RETURN blocks repaired
- Broken import/RETURN structure in warehouse modules reconstructed
- Meta versions, namespace, YAML formatting
- CI failures resolved across Python 3.11-3.13
- Galaxy import validation issues

### Changed
- Auto-formatted all modules with ruff
- Expanded ruff ignore list for compatibility

### Security
- SQL injection fix via string escaping in all modules

## [1.0.0] - 2026-05-15

### Added
- 104 modules covering full Snowflake data warehouse platform API
- CRUD + info module for every resource type
- Unit tests and CI pipeline
