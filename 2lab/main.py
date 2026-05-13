import math
import itertools
from functools import wraps
from typing import Iterable, Iterator, Callable, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection

Point = Tuple[float, float]
PolygonT = Tuple[Point, ...]


def close_poly(poly: PolygonT) -> PolygonT:
    if poly and poly[0] != poly[-1]:
        return poly + (poly[0],)
    return poly


def translate(poly: PolygonT, dx: float, dy: float) -> PolygonT:
    return tuple((x + dx, y + dy) for x, y in poly)


def rotate(poly: PolygonT, angle: float, origin: Point = (0.0, 0.0)) -> PolygonT:
    ox, oy = origin
    c, s = math.cos(angle), math.sin(angle)
    return tuple(
        (
            ox + (x - ox) * c - (y - oy) * s,
            oy + (x - ox) * s + (y - oy) * c
        )
        for x, y in poly
    )


def symmetry_x(poly: PolygonT, y0: float = 0.0) -> PolygonT:
    return tuple((x, 2 * y0 - y) for x, y in poly)


def symmetry_y(poly: PolygonT, x0: float = 0.0) -> PolygonT:
    return tuple((2 * x0 - x, y) for x, y in poly)


def reflect_origin(poly: PolygonT) -> PolygonT:
    return tuple((-x, -y) for x, y in poly)


def homothety(poly: PolygonT, k: float, origin: Point = (0.0, 0.0)) -> PolygonT:
    ox, oy = origin
    return tuple((ox + k * (x - ox), oy + k * (y - oy)) for x, y in poly)


def polygon_area(poly: PolygonT) -> float:
    p = close_poly(poly)
    s = 0.0
    for (x1, y1), (x2, y2) in zip(p, p[1:]):
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def polygon_perimeter(poly: PolygonT) -> float:
    p = close_poly(poly)
    return sum(math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in zip(p, p[1:]))


def edges(poly: PolygonT):
    p = close_poly(poly)
    return list(zip(p, p[1:]))


def side_lengths(poly: PolygonT):
    return [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in edges(poly)]


def angle_at(poly: PolygonT, i: int) -> float:
    n = len(poly)
    a = poly[(i - 1) % n]
    b = poly[i % n]
    c = poly[(i + 1) % n]
    v1 = (a[0] - b[0], a[1] - b[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    l1 = math.hypot(*v1)
    l2 = math.hypot(*v2)
    if l1 == 0 or l2 == 0:
        return 0.0
    cosv = max(-1.0, min(1.0, dot / (l1 * l2)))
    return math.acos(cosv)


def convex_hull_side(poly: PolygonT) -> bool:
    if len(poly) < 4:
        return True
    s = 0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        x3, y3 = poly[(i + 2) % n]
        cross = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)
        if cross != 0:
            curr = 1 if cross > 0 else -1
            if s == 0:
                s = curr
            elif s != curr:
                return False
    return True


def point_in_convex(poly: PolygonT, point: Point) -> bool:
    if len(poly) < 3:
        return False

    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    sign = None
    for i in range(len(poly)):
        c = cross(poly[i], poly[(i + 1) % len(poly)], point)
        if c != 0:
            curr = c > 0
            if sign is None:
                sign = curr
            elif sign != curr:
                return False
    return True


def rect_base(w=1.0, h=0.5) -> PolygonT:
    return ((0, 0), (w, 0), (w, h), (0, h))


def tri_base(a=1.0) -> PolygonT:
    h = a * math.sqrt(3) / 2
    return ((0, 0), (a / 2, h), (a, 0))


def tri_down_base(a=1.0) -> PolygonT:
    h = a * math.sqrt(3) / 2
    return ((0, h), (a / 2, 0), (a, h))


def hex_base(a=1.0) -> PolygonT:
    h = math.sqrt(3) * a / 2
    return ((0, h / 2), (a / 2, 0), (3 * a / 2, 0), (2 * a, h / 2), (3 * a / 2, h), (a / 2, h))


def rhombus_base(w=1.0, h=1.2) -> PolygonT:
    return ((0, 0), (w / 2, h / 2), (w, 0), (w / 2, -h / 2))


def gen_on_line(base: PolygonT, n: int, dx: float, dy: float) -> Iterator[PolygonT]:
    for i in range(n):
        yield translate(base, i * dx, i * dy)


def gen_rectangle(n: int, w=1.0, h=0.5, dx=1.2, dy=0.0) -> Iterator[PolygonT]:
    return gen_on_line(rect_base(w, h), n, dx, dy)


def gen_triangle(n: int, a=1.0, dx=1.2, dy=0.0, down=False) -> Iterator[PolygonT]:
    return gen_on_line(tri_down_base(a) if down else tri_base(a), n, dx, dy)


def gen_hexagon(n: int, a=1.0, dx=None, dy=0.0) -> Iterator[PolygonT]:
    if dx is None:
        dx = 2.5 * a
    return gen_on_line(hex_base(a), n, dx, dy)


def tr_translate(dx: float, dy: float) -> Callable[[PolygonT], PolygonT]:
    def f(poly: PolygonT) -> PolygonT:
        return translate(poly, dx, dy)
    return f


def tr_rotate(angle: float, origin: Point = (0.0, 0.0)) -> Callable[[PolygonT], PolygonT]:
    def f(poly: PolygonT) -> PolygonT:
        return rotate(poly, angle, origin)
    return f


def tr_symmetry(axis: str = "x", offset: float = 0.0) -> Callable[[PolygonT], PolygonT]:
    if axis == "x":
        return lambda poly: symmetry_x(poly, offset)
    if axis == "y":
        return lambda poly: symmetry_y(poly, offset)
    raise ValueError("axis must be 'x' or 'y'")


def tr_homothety(k: float, origin: Point = (0.0, 0.0)) -> Callable[[PolygonT], PolygonT]:
    def f(poly: PolygonT) -> PolygonT:
        return homothety(poly, k, origin)
    return f


def flt_convex_polygon(poly: PolygonT) -> bool:
    return convex_hull_side(poly)


def flt_angle_point(index: int, min_angle: float) -> Callable[[PolygonT], bool]:
    def f(poly: PolygonT) -> bool:
        if not poly:
            return False
        return angle_at(poly, index % len(poly)) >= min_angle
    return f


def flt_square(max_area: float) -> Callable[[PolygonT], bool]:
    return lambda poly: polygon_area(poly) < max_area


def flt_short_side(max_len: float) -> Callable[[PolygonT], bool]:
    return lambda poly: min(side_lengths(poly)) < max_len


def flt_point_inside(point: Point) -> Callable[[PolygonT], bool]:
    def f(poly: PolygonT) -> bool:
        return flt_convex_polygon(poly) and point_in_convex(poly, point)
    return f


def flt_polygon_angles_inside(reference: PolygonT) -> Callable[[PolygonT], bool]:
    ref_angles = [angle_at(reference, i) for i in range(len(reference))]
    def f(poly: PolygonT) -> bool:
        if not flt_convex_polygon(poly):
            return False
        poly_angles = [angle_at(poly, i) for i in range(len(poly))]
        return any(any(abs(a - b) < 1e-6 for b in poly_angles) for a in ref_angles)
    return f


def decorate_transform(transform: Callable[[PolygonT], PolygonT]):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            new_args = []
            for a in args:
                if isinstance(a, Iterable) and not isinstance(a, (tuple, str)):
                    new_args.append(map(transform, a))
                else:
                    new_args.append(a)
            return func(*new_args, **kwargs)
        return wrapper
    return dec


def decorate_filter(pred: Callable[[PolygonT], bool]):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            new_args = []
            for a in args:
                if isinstance(a, Iterable) and not isinstance(a, (tuple, str)):
                    new_args.append(filter(pred, a))
                else:
                    new_args.append(a)
            return func(*new_args, **kwargs)
        return wrapper
    return dec


def agr_origin_nearest(acc, poly: PolygonT):
    cand = min(poly, key=lambda p: math.hypot(p[0], p[1]))
    if acc is None:
        return cand
    return acc if math.hypot(acc[0], acc[1]) <= math.hypot(cand[0], cand[1]) else cand


def agr_max_side(acc, poly: PolygonT):
    cand = max(((math.hypot(b[0] - a[0], b[1] - a[1]), (a, b)) for a, b in edges(poly)), key=lambda t: t[0])
    if acc is None:
        return cand
    return acc if acc[0] >= cand[0] else cand


def agr_min_area(acc, poly: PolygonT):
    cand = (polygon_area(poly), poly)
    if acc is None:
        return cand
    return acc if acc[0] <= cand[0] else cand


def agr_perimeter(acc, poly: PolygonT):
    return (acc or 0) + polygon_perimeter(poly)


def agr_area(acc, poly: PolygonT):
    return (acc or 0) + polygon_area(poly)


def zip_polygons(*iters: Iterable[PolygonT]) -> Iterator[PolygonT]:
    for parts in zip(*iters):
        yield tuple(itertools.chain.from_iterable(parts))


def count_2D(it: Iterable, n: int = None):
    for i, x in enumerate(it):
        if n is not None and i >= n:
            break
        yield i, x


def zip_tuple(a: tuple, b: tuple) -> tuple:
    return tuple(itertools.chain.from_iterable(zip(a, b)))


def visualize(polygons: Iterable[PolygonT], title: str = "", ax=None, color="none", edgecolor="black"):
    polys = list(polygons)
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    patches = [MplPolygon(close_poly(p), closed=True) for p in polys]
    pc = PatchCollection(patches, facecolor=color, edgecolor=edgecolor, linewidth=1.0)
    ax.add_collection(pc)

    xs = [x for p in polys for x, y in p]
    ys = [y for p in polys for x, y in p]
    if xs and ys:
        mx = (max(xs) - min(xs)) * 0.15 + 1
        my = (max(ys) - min(ys)) * 0.15 + 1
        ax.set_xlim(min(xs) - mx, max(xs) + mx)
        ax.set_ylim(min(ys) - my, max(ys) + my)

    ax.axhline(0, color="gray", linewidth=0.8)
    ax.axvline(0, color="gray", linewidth=0.8)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title)
    ax.grid(False)
    return ax


def demo_rows():
    fig, axs = plt.subplots(3, 1, figsize=(10, 7))
    visualize(gen_rectangle(8, w=0.8, h=0.5, dx=1.0), "a) rectangles", axs[0])
    visualize(gen_triangle(8, a=0.8, dx=1.0), "b) triangles", axs[1])
    visualize(gen_hexagon(5, a=0.7, dx=2.5), "c) hexagons", axs[2])
    plt.tight_layout()
    plt.show()


def demo_transformations():
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))

    base = list(gen_rectangle(7, w=0.7, h=0.35, dx=0.95))
    ribbon1 = [tr_rotate(math.radians(30))(tr_translate(-2.5, -1.0)(p)) for p in base]
    ribbon2 = [tr_rotate(math.radians(30))(tr_translate(-2.5, -0.2)(p)) for p in base]
    ribbon3 = [tr_rotate(math.radians(30))(tr_translate(-2.5, 0.6)(p)) for p in base]
    visualize(ribbon1 + ribbon2 + ribbon3, "a) parallel ribbons", axs[0, 0])

    def make_ribbon(polys, angle, shift):
        return [tr_translate(*shift)(tr_rotate(angle)(p)) for p in polys]

    base2 = list(gen_rectangle(7, w=0.7, h=0.35, dx=1.0))
    ribbon_a = make_ribbon(base2, math.radians(30), (-2.5, -1.2))
    ribbon_b = make_ribbon(base2, math.radians(-30), (-1.2, 1.0))
    visualize(ribbon_a + ribbon_b, "b) intersecting ribbons", axs[0, 1])

    up = [tr_translate(-3.2, 1.2)(p) for p in gen_triangle(7, a=0.7, dx=0.95, down=True)]
    down = [tr_symmetry("x", 0)(p) for p in up]
    visualize(up + down, "c) symmetric triangle ribbons", axs[1, 0])

    band1 = []
    band2 = []

    for i in range(6):
        k = 1.10 - 0.10 * i

        p1 = rect_base(0.85, 0.28)
        p1 = tr_homothety(k)(p1)
        p1 = tr_rotate(math.radians(25))(p1)
        p1 = tr_translate(-5.0 + i * 0.5, -4.0 + i * 0.4)(p1)
        band1.append(p1)

        p2 = rect_base(0.85, 0.28)
        p2 = tr_homothety(k)(p2)
        p2 = tr_rotate(math.radians(25))(p2)
        p2 = tr_translate(1.5 + i * 0.5, 1.2 + i * 0.4)(p2)
        band2.append(p2)

    visualize(band1 + band2, "d) diagonal bands", axs[1, 1])

    plt.tight_layout()
    plt.show()


def demo_triangle_to_rhombus():
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))

    left = [
        tr_translate(-3.0 + i * 1.0, 0.8)(p)
        for i, p in enumerate(gen_triangle(6, a=0.8, dx=1.0, down=False))
    ]
    left += [
        tr_translate(-3.0 + i * 1.0, -0.8)(p)
        for i, p in enumerate(gen_triangle(6, a=0.8, dx=1.0, down=True))
    ]
    visualize(left, "before", axs[0])

    right = [
        tr_translate(-3.0 + i * 1.0, 0.0)(rhombus_base(0.8, 1.2))
        for i in range(6)
    ]
    visualize(right, "after", axs[1])

    plt.tight_layout()
    plt.show()


def demo_filter_six_figures():
    polys = list(itertools.islice(gen_rectangle(20, w=0.8, h=0.3, dx=1.0), 20))
    selected = list(itertools.islice(filter(flt_square(0.5), polys), 6))
    visualize(selected, "six filtered figures")


def demo_filter_short_sides():
    polys = [tr_homothety(0.5 + 0.1 * i)(rect_base(1.0, 0.5)) for i in range(15)]
    selected = list(filter(flt_short_side(0.9), polys))
    selected = selected[:4]
    visualize(selected, "filtered by short side")


def demo_filter_intersections():
    polys = []
    for i in range(15):
        p = rect_base(1.0, 0.4)
        p = tr_rotate(math.radians(i * 12))(p)
        p = tr_translate(math.cos(i) * 0.2, math.sin(i) * 0.2)(p)
        polys.append(p)
    selected = list(filter(flt_convex_polygon, polys))
    visualize(selected, "filtered intersecting-like figures")


if __name__ == "__main__":
    demo_rows()
    demo_transformations()
    demo_triangle_to_rhombus()
    demo_zip()
    demo_filter_six_figures()
    demo_filter_short_sides()
    demo_filter_intersections()
