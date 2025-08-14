"""Base command handler class for CLI commands."""

import argparse
from typing import Dict, Any


class CommandHandler:
    """Base class for command handlers."""
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command and return results."""
        raise NotImplementedError
