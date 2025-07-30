#!/usr/bin/env python3

import sys
from src.yt2mp3.cli import CLI


def main():
    try:
        cli = CLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()