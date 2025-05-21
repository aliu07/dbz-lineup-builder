import argparse
import questionary
from core.utils import Utils
from core.lineup_builder import LineupBuilder
from pprint import pprint

if __name__ == '__main__':
    # Init arg parser
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", type=str, help="Name of JSON file containing all paddler information")
    parser.add_argument("std_boats", type=int, help="Number of standard boats (e.g., 2)")
    parser.add_argument("small_boats", type=int, help="Number of small boats (e.g., 1)")
    args = parser.parse_args()

    # Parse paddler data
    paddlers = Utils.get_paddlers(args.json_file)

    # Select all absent paddlers
    paddler_names = sorted([p.name for p in paddlers])

    absent_paddler_names = questionary.checkbox(
        "Select absent paddlers:",
        choices=paddler_names,
    ).ask()

    Utils.remove_absent_paddlers(absent_paddler_names, paddlers)

    pprint(absent_paddler_names)

    # Generate lineups
    print(f"Init session for {args.std_boats} standard boat(s) and {args.small_boats} small boat(s)")

    builder = LineupBuilder(
        paddlers = paddlers,
        std_boat_count = args.std_boats,
        small_boat_count = args.small_boats,
    )

    builder.generate_lineups()
