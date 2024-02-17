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
    """ Base case of the recursive algorithm.
    """
    
    if len(points) == 0:
        return []
    return points


def compute_hull(points: List[Point]) -> List[Point]:
    """
    Given a list of points, computes the convex hull around those points
    and returns only the points that are on the hull.
    """
    
    # Sort the points by clockwise angle from the centroid.
    sort_clockwise(points)
    
    # Base case
    if len(points) <= 3:
        return base_case_hull(points)
    
    # Divide the points into two halves.
    midpoint = len(points) // 2

    left_half = points[:midpoint]
    right_half = points[midpoint:]

    sort_clockwise(left_half)
    sort_clockwise(right_half)

    # Recursively compute the hulls of the two halves.
    left_hull = compute_hull(left_half)
    right_hull = compute_hull(right_half)

    # Merge the two hulls.
    return merge_hulls(left_hull, right_hull)


def merge_hulls(left_hull: List[Point], right_hull: List[Point]) -> List[Point]:
    """ Merges the two hulls into a single hull.
    """
    
    # Find the rightmost point of the left hull and the leftmost point of the right hull.
    leftmost_point = max(left_hull, key=lambda p: p[0])
    rightmost_point = min(right_hull, key=lambda p: p[0])
    
    # Find the upper tangent.
    upper_tangent = [leftmost_point, rightmost_point]
    while True:
        # Find the next point on the left hull.
        next_point = left_hull[(left_hull.index(upper_tangent[0]) + 1) % len(left_hull)]
        
        # If the next point is to the right of the line from the current upper tangent to the rightmost point of the right hull, then we have found the upper tangent.
        if is_counter_clockwise(upper_tangent[0], upper_tangent[1], next_point):
            upper_tangent[0] = next_point
        else:
            break
    
    # Find the lower tangent.
    lower_tangent = [leftmost_point, rightmost_point]
    while True:
        # Find the next point on the right hull.
        next_point = right_hull[(right_hull.index(lower_tangent[1]) + 1) % len(right_hull)]
        
        # If the next point is to the left of the line from the current lower tangent to the leftmost point of the left hull, then we have found the lower tangent.
        if is_clockwise(lower_tangent[1], lower_tangent[0], next_point):
            lower_tangent[1] = next_point
        else:
            break
    
    # Merge the two hulls using the upper and lower tangents.
    merged_hull = []
    for point in left_hull:
        if is_counter_clockwise(upper_tangent[0], lower_tangent[1], point):
            merged_hull.append(point)
    for point in right_hull:
        if is_counter_clockwise(upper_tangent[0], lower_tangent[1], point):
            merged_hull.append(point)

    print("Merged hull:", merged_hull)

    return merged_hull