from cgshop2027_pyutils.io import read_instance
from cgshop2027_pyutils.schemas import CGSHOP2027Solution, CutterTour
from cgshop2027_pyutils.grid import rasterize, rasterize_ring
from cgshop2027_pyutils.verify import check_for_errors
from cgshop2027_pyutils.visualize import create_solution_plot

import matplotlib.pyplot as plt


INSTANCE_PATH = "test_instances1/iso_725k_1813_3d6.instance.json"
SOLUTION_PATH = "basic_solution.solution.json"


def make_serpentine(x_min, x_max, y_min, y_max):
    """Visit every lattice point in a rectangular grid."""

    points = []

    # We want the final point to have the same x-coordinate
    # as the first point so that the closing edge is vertical.
    height = y_max - y_min + 1

    if height % 2 == 1:
        y_max += 1

    for row, y in enumerate(range(y_min, y_max + 1)):

        if row % 2 == 0:
            # left -> right
            xs = range(x_min, x_max + 1)
        else:
            # right -> left
            xs = range(x_max, x_min - 1, -1)

        for x in xs:
            points.append((x, y))

    return points


def solve(instance):

    # ---------------------------------------------------------
    # 1. Convert the region and cutter to sets of unit cells
    # ---------------------------------------------------------

    region = rasterize(instance.region_to_cover)
    cutter = rasterize_ring(instance.cutter)

    center_x, center_y = instance.cutter_center

    # Pick any cell belonging to the cutter.
    cutter_anchor = next(cutter.cells())

    ax, ay = cutter_anchor

    # ---------------------------------------------------------
    # 2. Find a cutter-center position for every region cell
    # ---------------------------------------------------------

    required_centers = []

    for rx, ry in region.cells():

        cx = rx + center_x - ax
        cy = ry + center_y - ay

        required_centers.append((cx, cy))

    # ---------------------------------------------------------
    # 3. Put all required centers inside one bounding rectangle
    # ---------------------------------------------------------

    xs = [p[0] for p in required_centers]
    ys = [p[1] for p in required_centers]

    x_min = min(xs)
    x_max = max(xs)
    y_min = min(ys)
    y_max = max(ys)

    # ---------------------------------------------------------
    # 4. Traverse the rectangle in serpentine order
    # ---------------------------------------------------------

    active_tour = make_serpentine(
        x_min,
        x_max,
        y_min,
        y_max,
    )

    tour_x = [p[0] for p in active_tour]
    tour_y = [p[1] for p in active_tour]

    # ---------------------------------------------------------
    # 5. Other cutters stay stationary
    # ---------------------------------------------------------

    stationary_x = [active_tour[0][0]]
    stationary_y = [active_tour[0][1]]

    tours = [
        CutterTour(x=tour_x, y=tour_y),
        CutterTour(x=stationary_x, y=stationary_y),
        CutterTour(x=stationary_x, y=stationary_y),
    ]

    return CGSHOP2027Solution(
        instance_uid=instance.instance_uid,
        tours=tours,
        meta={
            "algorithm": "basic rectangular serpentine baseline"
        },
    )


def main():

    # Read instance
    instance = read_instance(INSTANCE_PATH)

    # Construct solution
    solution = solve(instance)

    # Print objective
    print("Instance:", instance.instance_uid)
    print("Number of cutters:", instance.number_of_cutters)

    for i, tour in enumerate(solution.tours):
        print(
            f"Cutter {i + 1}: "
            f"{len(tour.x)} points, "
            f"length = {tour.length}"
        )

    print("Makespan:", solution.max_tour_length)

    # ---------------------------------------------------------
    # Verify
    # ---------------------------------------------------------

    errors = check_for_errors(instance, solution)

    if errors:
        print("\nSOLUTION INVALID")
        for error in errors:
            print(" -", error)
    else:
        print("\nSOLUTION VALID!")

    # ---------------------------------------------------------
    # Save solution
    # ---------------------------------------------------------

    with open(SOLUTION_PATH, "w") as f:
        f.write(solution.model_dump_json(indent=2))

    print("\nSaved:", SOLUTION_PATH)

    # ---------------------------------------------------------
    # Visualize
    # ---------------------------------------------------------

    fig = create_solution_plot(instance, solution)
    plt.show()


if __name__ == "__main__":
    main()