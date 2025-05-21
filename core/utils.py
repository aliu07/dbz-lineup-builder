import json
from models.paddler import Paddler

class Utils:
    @staticmethod
    def get_seat_order(capacity: int) -> list[int]:
        """
        Returns a balanced seat order for the given boat capacity.
        Supports 5 (small boat) and 10 (standard boat) paddlers.
        """
        seat_orders = {
            5: [2, 1, 3, 0, 4], # Small boat
            10: [4, 5, 3, 6, 2, 7, 1, 8, 0, 9], # Standard boat
        }

        return seat_orders.get(capacity, [])

    @staticmethod
    def get_paddlers(json_filename: str):
        paddlers = set()

        try:
            with open(json_filename, "r", encoding="utf-8") as json_file:
                contents = json.load(json_file)

                for elmt in contents:
                    paddlers.add(Paddler(**elmt))
        except FileNotFoundError:
            print(f"The file {json_filename} does not exist")
        except json.JSONDecodeError:
            print(f"The file {json_filename}'s content format is invalid")

        return paddlers

    @staticmethod
    def remove_absent_paddlers(absent_paddler_names: set[str], paddlers: set[Paddler]):
        to_remove = {p for p in paddlers if p.name in absent_paddler_names}
        paddlers.difference_update(to_remove)
