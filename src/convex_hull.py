import math
import sys
from typing import List
from typing import Tuple

EPSILON = sys.float_info.epsilon
Point = Tuple[int, int]


def y_intercept(p1: Point, p2: Point, x: int) -> float:
    """
    Given two points, p1 and p2, an x coordinate from a vertical line,
    compute and return the the y-intercept of the line segment p1->p2
    with the vertical line passing through x.
    """
    x1, y1 = p1
    x2, y2 = p2
    slope = (y2 - y1) / (x2 - x1)
    return y1 + (x - x1) * slope


def triangle_area(a: Point, b: Point, c: Point) -> float:
    """
    Given three points a,b,c,
    computes and returns the area defined by the triangle a,b,c.
    Note that this area will be negative if a,b,c represents a clockwise sequence,
    positive if it is counter-clockwise,
    and zero if the points are collinear.
    """
    ax, ay = a
    bx, by = b
    cx, cy = c
    return ((cx - bx) * (by - ay) - (bx - ax) * (cy - by)) / 2


def is_clockwise(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c represents a clockwise sequence
    (subject to floating-point precision)
    """
    return triangle_area(a, b, c) < -EPSILON


def is_counter_clockwise(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c represents a counter-clockwise sequence
    (subject to floating-point precision)
    """
    return triangle_area(a, b, c) > EPSILON


def collinear(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c are collinear
    (subject to floating-point precision)
    """
    return abs(triangle_area(a, b, c)) <= EPSILON


def sort_clockwise(points: List[Point]):
    """
    Sorts `points` by ascending clockwise angle from +x about the centroid,
    breaking ties first by ascending x value and then by ascending y value.

    The order of equal points is not modified

    Note: This function modifies its argument
    """
    # Trivial cases don't need sorting, and this dodges divide-by-zero errors
    if len(points) < 2:
        return

    # Compute the centroid
    centroid_x = sum(p[0] for p in points) / len(points)
    centroid_y = sum(p[1] for p in points) / len(points)

    # Sort by ascending clockwise angle from +x, breaking ties with ^x then ^y
    def sort_key(point: Point):
        angle = math.atan2(point[1] - centroid_y, point[0] - centroid_x)
        normalized_angle = (angle + math.tau) % math.tau
        return (normalized_angle, point[0], point[1])

    # Sort the points
    points.sort(key=sort_key)


def base_case_hull(points: List[Point]) -> List[Point]:
    """
    Base case of the recursive algorithm.
    """

    if len(points) <= 3:
        return points

    # Sort the points by ascending x value, breaking ties by ascending y value.
    points.sort()

    # Initialize the convex hull.
    hull = []

    # Initialize our control variables.
    p = 0
    q = None

    # Iterate through the points to find the convex hull.
    while True:
        hull.append(points[p])
        q = (p + 1) % len(points)

        for i in range(len(points)):
            if is_counter_clockwise(points[p], points[i], points[q]):
                q = i

        p = q

        if p == 0:
            break
    
    return hull


def merge_hulls(L: List[Point], R: List[Point]) -> List[Point]:
    """
    Given two lists of points, L and R, each of which represents a convex hull,
    computes and returns the convex hull of the combined points in L and R.
    """

    # Sort the points in L and R by ascending x value, breaking ties by ascending y value.
    sort_clockwise(L)
    sort_clockwise(R)
    
    # Print the hulls for debugging purposes.
    #print("L:", L)
    #print("R:", R)

    # Initialize the convex hull.
    result = []

    # Initialize our control variables.
    right_of_left_idx = L.index(max(L, key=lambda p: p[0]))
    left_of_right_idx = R.index(min(R, key=lambda p: p[0]))

    # Print the indices for debugging purposes.
    #print("Right of left:", right_of_left_idx)
    #print("Left of right:", left_of_right_idx)

    # Initialize the upper tangent.
    upper_tangent = (right_of_left_idx, left_of_right_idx)

    # Find the upper tangent.
    while True:
        right_progress = False
        left_progress = False
        
        while True:
            next_right = (upper_tangent[1] + 1) % len(R)

            if is_counter_clockwise(L[upper_tangent[0]], R[upper_tangent[1]], R[next_right]):
                upper_tangent = (upper_tangent[0], next_right)
                right_progress = True
            else:
                break
            
        while True:
            next_left = (upper_tangent[0] - 1) % len(L)

            if is_clockwise(R[upper_tangent[1]], L[upper_tangent[0]], L[next_left]):
                upper_tangent = (next_left, upper_tangent[1])
                left_progress = True
            else:
                break
            
        if not right_progress and not left_progress:
            break
        
    #print("Upper tangent:", upper_tangent)

    # Initialize the lower tangent.
    lower_tangent = (right_of_left_idx, left_of_right_idx)

    # Find the lower tangent.
    while True:
        right_progress = False
        left_progress = False
        
        while True:
            next_right = (lower_tangent[1] - 1) % len(R)

            if is_clockwise(L[lower_tangent[0]], R[lower_tangent[1]], R[next_right]):
                lower_tangent = (lower_tangent[0], next_right)
                right_progress = True
            else:
                break
            
        while True:
            next_left = (lower_tangent[0] + 1) % len(L)

            if is_counter_clockwise(R[lower_tangent[1]], L[lower_tangent[0]], L[next_left]):
                lower_tangent = (next_left, lower_tangent[1])
                left_progress = True
            else:
                break
            
        if not right_progress and not left_progress:
            break
    
    #print("Lower tangent:", lower_tangent)

    # Merge Left
    for i in range(lower_tangent[0], upper_tangent[0] + 1):
        result.append(L[i])
        
    # Merge Right
    if lower_tangent[1] > upper_tangent[1]:
        for i in range(upper_tangent[1], lower_tangent[1] + 1):
            result.append(R[i])
    else:
        for i in range(upper_tangent[1], len(R)):
            result.append(R[i])
        for i in range(0, lower_tangent[1] + 1):
            result.append(R[i])

    #print("Result:", result)
    #print()

    return result


def compute_hull(points: List[Point]) -> List[Point]:
    """
    Given a list of points, computes the convex hull around those points
    and returns only the points that are on the hull.
    """
    
    # Sort the points by ascending x value, breaking ties by ascending y value.
    points = list(set(points))
    #print("Points:", points)
    points.sort()
    #print("Points:", points)

    # Base case: if there are 5 or fewer points, we call the base case function.
    if len(points) <= 5:
        return base_case_hull(points)
    
    # Split the points into two halves (L & R).
    middle = len(points) // 2
    L = points[:middle]
    R = points[middle:]

    # Recursively compute the hulls of the two halves.
    L = compute_hull(L)
    R = compute_hull(R)

    # Merge the two hulls together.
    return merge_hulls(L, R)
