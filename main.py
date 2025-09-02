#!/usr/bin/env python3
"""
Main entry point for the Interactive Storytelling Assistant.

This script provides both command-line and web interface options.
"""

import sys
import argparse
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from storytelling.core import main as cli_main
from gradio_app import main as web_main


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Interactive Storytelling Assistant for Kids (6-9 years old)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --web          # Launch web interface (default)
  python main.py --cli          # Launch command-line interface
  python main.py --help         # Show this help message
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--web", 
        action="store_true", 
        default=True,
        help="Launch web interface using Gradio (default)"
    )
    group.add_argument(
        "--cli", 
        action="store_true",
        help="Launch command-line interface"
    )
    
    args = parser.parse_args()
    
    if args.cli:
        print("🌟 Starting Interactive Storytelling Assistant (CLI mode)")
        cli_main()
    else:
        print("🌟 Starting Interactive Storytelling Assistant (Web mode)")
        print("🌐 Opening web interface...")
        web_main()


if __name__ == "__main__":
    main()