from models.paddler import Paddler
from models.boats import Boat, SmallBoat, StandardBoat
from typing import List, Optional
from core.utils import Utils

class LineupBuilder:
    def __init__(self, paddlers: set[Paddler], std_boat_count: int, small_boat_count: int):
        self.paddlers = paddlers
        self.boats = []
        # Add small boats first to prioritize weight balance
        for id in range(small_boat_count):
            self.boats.append(SmallBoat(id+1))
        # Add standard boats
        for id in range(std_boat_count):
            self.boats.append(StandardBoat(id+1))

    def generate_lineups(self):
            # Assign paddlers to boats
            for boat in self.boats:
                self.assign_paddlers_to_boat(
                    boat,
                    self.paddlers
                )

            # Balance each boat with spares
            for boat in self.boats:
                self.balance_with_spares(boat)

            for boat in self.boats:
                boat_type = 'Standard' if isinstance(boat, StandardBoat) else 'Small'

                print(f"\n🚣 {boat_type} Boat {boat.id} Lineup:")

                print(f"  Left ({len(boat.left)}):")
                for i in range(0, len(boat.left), 3):
                    print("\t" + ", ".join(p.name for p in list(boat.left)[i:i+3]))

                print(f"  Right ({len(boat.right)}):")
                for i in range(0, len(boat.right), 3):
                    print("\t" + ", ".join(p.name for p in list(boat.right)[i:i+3]))

                lw = sum(p.weight for p in boat.left)
                rw = sum(p.weight for p in boat.right)
                heavy_side = 'left heavy' if lw > rw else 'right heavy' if rw > lw else 'equally balanced'

                print(f"  Weight Diff: {abs(lw - rw):.2f} lbs ({heavy_side})")

            # Print spares (leftover paddlers)
            spare_left = [p for p in self.paddlers if p.side == 'left']
            spare_right = [p for p in self.paddlers if p.side == 'right']
            spare_ambi = [p for p in self.paddlers if p.side == 'ambi']

            print("\n🚨 Spare Paddlers:")
            print(f"  Left ({len(spare_left)}):")
            for i in range(0, len(spare_left), 3):
                print("\t" + ", ".join(p.name for p in list(spare_left)[i:i+3]))
            print(f"  Right ({len(spare_right)}):")
            for i in range(0, len(spare_right), 3):
                print("\t" + ", ".join(p.name for p in list(spare_right)[i:i+3]))
            print(f"  Ambi ({len(spare_ambi)}):")
            for i in range(0, len(spare_ambi), 3):
                print("\t" + ", ".join(p.name for p in list(spare_ambi)[i:i+3]))


    def assign_paddlers_to_boat(self, boat: Boat, paddlers: set[Paddler]) -> None:
        # Target number of guys and girls for each side
        target_males = boat.capacity_per_side // 2
        target_females = boat.capacity_per_side - target_males

        # Fill left side of boat
        left_males = sorted({p for p in paddlers if p.gender == 'male' and p.side == 'left'}, key=lambda p: p.weight, reverse=True)
        left_females = sorted({p for p in paddlers if p.gender == 'female' and p.side == 'left'}, key=lambda p: p.weight, reverse=True)
        ambi_males = sorted({p for p in paddlers if p.gender == 'male' and p.side == 'ambi'}, key=lambda p: p.weight, reverse=True)
        ambi_females = sorted({p for p in paddlers if p.gender == 'female' and p.side == 'ambi'}, key=lambda p: p.weight, reverse=True)

        selected_lefty_males = self.fill_side(target_males, left_males, ambi_males)
        selected_lefty_females = self.fill_side(target_females, left_females, ambi_females)

        # Fill right side of boat
        # Need to recompute ambis since some might have been removed from filling left side
        right_males = sorted({p for p in paddlers if p.gender == 'male' and p.side == 'right'}, key=lambda p: p.weight, reverse=True)
        right_females = sorted({p for p in paddlers if p.gender == 'female' and p.side == 'right'}, key=lambda p: p.weight, reverse=True)
        ambi_males = sorted({p for p in paddlers if p.gender == 'male' and p.side == 'ambi'}, key=lambda p: p.weight, reverse=True)
        ambi_females = sorted({p for p in paddlers if p.gender == 'female' and p.side == 'ambi'}, key=lambda p: p.weight, reverse=True)

        selected_righty_males = self.fill_side(target_males, right_males, ambi_males)
        selected_righty_females = self.fill_side(target_females, right_females, ambi_females)

        # Perform local swaps between ambis to see if weight diff can be minimized
        left, right = self.optimize_ambi_swaps(selected_lefty_males + selected_lefty_females, selected_righty_males + selected_righty_females)

        # Reorder by weight distribution (heaviest in the middle)
        boat.left = self.reorder_side_by_weight(left, boat.capacity_per_side)
        boat.right = self.reorder_side_by_weight(right, boat.capacity_per_side)

    def fill_side(self, capacity: int, primary_paddlers: list[Paddler], ambi_paddlers: list[Paddler]) -> list[Paddler]:
        selected = []
        remaining_capacity = capacity

        for p in primary_paddlers:
            if remaining_capacity > 0:
                selected.append(p)
                self.paddlers.remove(p)
                remaining_capacity -= 1

        for p in ambi_paddlers:
            if remaining_capacity > 0:
                selected.append(p)
                self.paddlers.remove(p)
                remaining_capacity -= 1

        return selected

    def optimize_ambi_swaps(self, left: list[Paddler], right: list[Paddler]) -> tuple[list[Paddler], list[Paddler]]:
        def total_weight(paddlers):
            return sum(p.weight for p in paddlers)

        def weight_diff(l, r):
            return abs(total_weight(l) - total_weight(r))

        best_diff = weight_diff(left, right)
        improved = True

        while improved:
            improved = False
            # Find all ambis on each side
            ambis_left = [p for p in left if p.side == 'ambi']
            ambis_right = [p for p in right if p.side == 'ambi']

            for i, p_left in enumerate(ambis_left):
                for j, p_right in enumerate(ambis_right):
                    # Try swapping p_left and p_right
                    new_left = left.copy()
                    new_right = right.copy()

                    # Find and swap
                    idx_left = new_left.index(p_left)
                    idx_right = new_right.index(p_right)

                    new_left[idx_left] = p_right
                    new_right[idx_right] = p_left

                    new_diff = weight_diff(new_left, new_right)

                    if new_diff < best_diff:
                        left = new_left
                        right = new_right
                        best_diff = new_diff
                        improved = True
                        break
                if improved:
                    break

        return left, right


    def balance_with_spares(self, boat):
        def total_weight(paddlers):
            return sum(p.weight for p in paddlers)

        def weight_diff(left, right):
            return abs(total_weight(left) - total_weight(right))

        lw = total_weight(boat.left)
        rw = total_weight(boat.right)

        if abs(lw - rw) <= 50:
            return  # Already balanced enough

        heavy_side = 'left' if lw > rw else 'right'
        side_paddlers = boat.left if heavy_side == 'left' else boat.right
        spare_pool = [p for p in self.paddlers if p.side == 'left'] if heavy_side == 'left' else [p for p in self.paddlers if p.side == 'right']
        improved = True

        while improved:
            improved = False
            best_swap = None
            best_cost = weight_diff(boat.left, boat.right)

            for i, boat_paddler in enumerate(side_paddlers):
                for spare in spare_pool:
                    # Try swapping boat paddler with spare
                    temp_side = side_paddlers[:]
                    temp_side[i] = spare

                    temp_left = temp_side if heavy_side == 'left' else boat.left
                    temp_right = temp_side if heavy_side == 'right' else boat.right

                    new_cost = weight_diff(temp_left, temp_right)

                    if new_cost < best_cost:
                        best_cost = new_cost
                        best_swap = (i, spare, boat_paddler)

            if best_swap:
                i, spare, boat_paddler = best_swap
                side_paddlers[i] = spare
                spare_pool.remove(spare)

                if heavy_side == 'left':
                    boat.left = side_paddlers
                    self.paddlers.add(boat_paddler)
                    self.paddlers.remove(spare)
                else:
                    boat.right = side_paddlers
                    self.paddlers.add(boat_paddler)
                    self.paddlers.remove(spare)

                improved = True

    def reorder_side_by_weight(self, paddlers: list[Paddler], capacity: int) -> list[Paddler]:
        paddlers_sorted = sorted(paddlers, key=lambda p: p.weight, reverse=True)
        seat_order = Utils.get_seat_order(capacity)
        ordered: List[Optional[Paddler]] = [None] * capacity

        for idx, paddler in zip(seat_order, paddlers_sorted):
            ordered[idx] = paddler

        return [p for p in ordered if p is not None]
