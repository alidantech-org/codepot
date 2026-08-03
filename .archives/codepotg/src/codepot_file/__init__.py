"""CodepotG configuration loading and task execution."""

from archives.codepotg.src.codepot_file.loader import load_codepotg_config, resolve_codepotg_config
from archives.codepotg.src.codepot_file.models import (
    CodepotCommand as CodepotgCommand,
)
from archives.codepotg.src.codepot_file.models import (
    CodepotFile as CodepotgConfig,
)
from archives.codepotg.src.codepot_file.models import (
    CodepotTask as CodepotgTask,
)

__all__ = [
    "CodepotgCommand",
    "CodepotgConfig",
    "CodepotgTask",
    "load_codepotg_config",
    "resolve_codepotg_config",
]
