import argparse
import asyncio

from .reader import list_batteries, main_async


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read telemetry from visible LiTime Bluetooth batteries."
    )

    parser.add_argument(
        "--output",
        choices=["human", "json", "rawjson"],
        default="human",
        help="Output format. Use json for parsed rows, rawjson for packet analysis.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Polling interval in seconds.",
    )

    parser.add_argument(
        "--scan-timeout",
        type=float,
        default=10.0,
        help="BLE scan timeout in seconds.",
    )

    parser.add_argument(
        "--read-timeout",
        type=float,
        default=10.0,
        help="Timeout for one-shot reads.",
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Read one state from each visible battery and exit.",
    )

    parser.add_argument(
        "--battery-name",
        type=str,
        help="Filter visible batteries by name substring.",
    )

    parser.add_argument(
        "--address",
        type=str,
        help="Filter visible batteries by Bluetooth address.",
    )

    parser.add_argument(
        "--list-batteries",
        action="store_true",
        help="Print discovered LiTime battery names only and exit.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        if args.list_batteries:
            asyncio.run(list_batteries(args.scan_timeout))
            return

        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("User-terminated")


if __name__ == "__main__":
    main()
