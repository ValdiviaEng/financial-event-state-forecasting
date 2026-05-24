"""
Command-line entry-point package.

What this package should eventually provide:
- thin orchestration commands for each major pipeline stage,
- consistent argument naming across data, training, and evaluation commands,
- clear separation between command parsing and business logic,
- resolved-config loading,
- run folder creation,
- structured logging for each command.

Design rule:
- CLI files should call lower-level modules in `src.data`, `src.features`,
  `src.models`, and `src.split`.
- They should not become the place where core logic lives.
"""
