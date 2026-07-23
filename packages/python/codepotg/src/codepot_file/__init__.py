"""CodepotG configuration loading and task execution."""

from codepot_file.loader import load_codepotg_config, resolve_codepotg_config
from codepot_file.models import (
    CodepotCommand as CodepotgCommand,
)
from codepot_file.models import (
    CodepotFile as CodepotgConfig,
)
from codepot_file.models import (
    CodepotTask as CodepotgTask,
)

__all__ = [
    "CodepotgCommand",
    "CodepotgConfig",
    "CodepotgTask",
    "load_codepotg_config",
    "resolve_codepotg_config",
]
