import math
from scipy import spatial


class _Coordinate:
    """
    Attributes:
        coord_x (int): Initial x coordinate of the region (top-left).
        coord_y (int): Initial y coordinate of the region (top-left).
    """
    def __init__(self, *args):
        self.array = tuple(int(i) for i in args)

    def __str__(self):
        return str(self.array)

    def __eq__(self, other):
        return self.array == other.array

    @property
    def coord_x(self):
        return self.array[0]

    @property
    def coord_y(self):
        return self.array[1]

    def distance(self, other):
        """
        Calculate distance to other coordinate
        """
        other = as_coordinate(other)

        dx = self.coord_x - other.coord_x
        dy = self.coord_y - other.coord_y
        return int(math.sqrt(dx**2 + dy**2))


class Region(_Coordinate):
    """
    Attributes:
        coord_x (int): Initial x coordinate of the region (top-left).
        coord_y (int): Initial y coordinate of the region (top-left).
        width (int): Width of the region.
        height (int): Height of the region.
    """
    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        return f"({self.array[0]}:{self.array[2]}, {self.array[1]}:{self.array[3]})"

    @property
    def width(self):
        return self.array[2]

    @property
    def height(self):
        return self.array[3]

    def translate(self, coord_x, coord_y):
        """
        Translate current coordinates to new coordinates

        Args:
            coord_x, coord_y: int

        Returns:
            Region - new object
        """
        return Region(
            self.coord_x + coord_x,
            self.coord_y + coord_y,
            self.width,
            self.height
        )

    def inside(self, *region):
        """
        Check this region is inside other region

        Args:
            other: array of int in order (coord_x, coord_y, width, height)

        Returns:
            boolean
        """

        coord_x_min = region[0]
        coord_x_max = region[0] + region[2]
        coord_y_min = region[1]
        coord_y_max = region[1] + region[3]

        return coord_x_min <= self.coord_x and self.coord_x + self.width <= coord_x_max and \
               coord_y_min <= self.coord_y and self.coord_y + self.height <= coord_y_max

    def outside(self, *region):
        """
        Check this region is outside other region

        Args:
            other: array of int in order (coord_x, coord_y, width, height)

        Returns:
            boolean
        """

        coord_x_min = region[0]
        coord_x_max = region[0] + region[2]
        coord_y_min = region[1]
        coord_y_max = region[1] + region[3]

        return (self.coord_x < coord_x_min and self.coord_x + self.width < coord_x_min) or \
               (self.coord_x > coord_x_max and self.coord_x + self.width > coord_x_max) or \
               (self.coord_y < coord_y_min and self.coord_y + self.height < coord_y_min) or \
               (self.coord_y > coord_y_max and self.coord_y + self.height > coord_y_max)

    def scale(self, scale=1):
        """
        Get new region that scale by value provided

        Args:
            scale: float|tuple(float, float) optional(df=1)
                Scale value(s)

        Returns:
            Region - new object
        """
        if isinstance(scale, float):
            return Region(
                int(self.coord_x * scale),
                int(self.coord_y * scale),
                int(self.width * scale),
                int(self.height * scale)
            )

        if isinstance(scale, tuple):
            return Region(
                int(self.coord_x * scale[0]),
                int(self.coord_y * scale[1]),
                int(self.width * scale[0]),
                int(self.height * scale[1])
            )

        return self

    def to_location(self):
        """
        Convert region to location

        Returns:
            Location
        """
        return Location(*self.array)

class Location(_Coordinate):
    """
    Attributes:
        coord_x (int): Initial x coordinate (top-left).
        coord_y (int): Initial y coordinate (top-left).
    """

    def translate(self, coord_x, coord_y):
        """
        Translate current coordinates to new coordinates

        Args:
            coord_x, coord_y: int

        Returns:
            Location - new object
        """
        return Location(
            self.coord_x + coord_x,
            self.coord_y + coord_y,
        )

    def inside(self, *region):
        """
        Check this location is inside other region

        Args:
            region: array of int in order (coord_x, coord_y, width, height)

        Returns:
            boolean
        """

        coord_x_min = region[0]
        coord_x_max = region[0] + region[2]
        coord_y_min = region[1]
        coord_y_max = region[1] + region[3]

        return coord_x_min <= self.coord_x and self.coord_x <= coord_x_max and \
               coord_y_min <= self.coord_y and self.coord_y <= coord_y_max

    def outside(self, *region):
        """
        Check this location is outside other region

        Args:
            region: array of int in order (coord_x, coord_y, width, height)

        Returns:
            boolean
        """

        coord_x_min = region[0]
        coord_x_max = region[0] + region[2]
        coord_y_min = region[1]
        coord_y_max = region[1] + region[3]

        return self.coord_x < coord_x_min or self.coord_x > coord_x_max or \
               self.coord_y < coord_y_min or self.coord_y > coord_y_max

    def scale(self, scale=1):
        """
        Get new location that scale by value provided

        Args:
            scale: float|tuple(float, float) optional(df=1)
                Scale value(s)

        Returns:
            Location - new object
        """
        if isinstance(scale, float):
            return Location(
                int(self.coord_x * scale),
                int(self.coord_y * scale),
            )

        if isinstance(scale, tuple):
            return Location(
                int(self.coord_x * scale[0]),
                int(self.coord_y * scale[1]),
            )

        return self

    def to_region(self, width, height):
        """
        Convert location to region

        Args:
            width, height: int

        Returns:
            Region
        """
        return Region(
            self.coord_x,
            self.coord_y,
            width,
            height)


def as_coordinate(coords):
    """
    Try convert coordinates to Location, Region
    """
    if isinstance(coords, (Region, Location)):
        return coords

    if len(coords) >= 4:
        return Region(*coords)

    if len(coords) >= 2:
        return Location(*coords)

    return None


def filter_coord(filter_func, coords, return_list=False):
    result_iter = filter(
        lambda x: filter_func(as_coordinate(x)), list(coords)
    )

    if return_list:
        return list(result_iter)

    return result_iter


def filter_similar_coords(coords, distance):
    """
    Filters out coordinates that are close to each other.

    Args:
        coords (array): An array containing the coordinates to be filtered.

    Returns:
        array: An array containing the filtered coordinates.
    """
    if len(coords) == 0:
        return []

    filtered_coords = [coords[0][:2]]

    for coord in coords:
        if spatial.KDTree(filtered_coords).query(coord[:2])[0] > distance:
            filtered_coords.append(coord[:2])

    results = []

    for filtered_coord in filtered_coords:
        mcoords = [coord for coord in coords if filtered_coord == coord[:2]]
        msizes = [coord[2] * coord[3] for coord in mcoords]
        d = dict(zip(mcoords, msizes))

        mcoord = min(d, key=d.get)
        results.append(mcoord)

    return results
