import argparse
import os
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Sze Yap Bot with an explicit local data directory.")
    parser.add_argument(
        "--data-dir",
        default=os.getenv("SZEYAP_DATA_DIR", "./.szeyap-bot-data"),
        help="Directory for runtime data, caches, and generated files.")
    return parser.parse_args()


def main():
    args = parse_args()
    data_dir = Path(args.data_dir).expanduser().resolve()
    os.environ["SZEYAP_DATA_DIR"] = str(data_dir)
    print(f"Using SZEYAP_DATA_DIR={data_dir}")

    from dictionary_bot import main as bot_main

    bot_main()


if __name__ == "__main__":
    main()