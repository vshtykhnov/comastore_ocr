"""Enhanced CLI module with better organization and command handling."""

import argparse
from typing import Dict, Any

from .process_images_handler import ProcessImagesHandler
from .sort_text_handler import SortTextHandler


class CLIApplication:
    """Main CLI application class."""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.command_handlers = {
            "process": ProcessImagesHandler,
            "sort": SortTextHandler,
        }
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all commands."""
        parser = argparse.ArgumentParser(
            description="ComaStore OCR - Enhanced command line interface",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s process
  %(prog)s sort
            """
        )
        
        subparsers = parser.add_subparsers(dest="cmd", required=True, help="Available commands")
        
        # Process images command
        p1 = subparsers.add_parser("process", help="Generate labels for images in directory")
        
        # Sort text command
        p2 = subparsers.add_parser("sort", help="Sort images using Tesseract + rules")
        
        return parser
    
    def run(self, args: list = None) -> Dict[str, Any]:
        """Run the CLI application."""
        parsed_args = self.parser.parse_args(args)
        
        if parsed_args.cmd not in self.command_handlers:
            print(f"❌ Unknown command: {parsed_args.cmd}")
            return {"status": "error", "error": f"Unknown command: {parsed_args.cmd}"}
        
        # Create and execute command handler
        handler_class = self.command_handlers[parsed_args.cmd]
        handler = handler_class(parsed_args)
        
        try:
            result = handler.execute()
            return result
        except KeyboardInterrupt:
            print("\n⚠️  Operation interrupted by user")
            return {"status": "interrupted"}
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {"status": "error", "error": str(e)}


def main():
    """Main entry point for the enhanced CLI."""
    app = CLIApplication()
    result = app.run()
    
    if result["status"] == "success":
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
