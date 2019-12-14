from scipy import spatial


class _Coordinate:
    """
    Attributes:
        coord_x (int): Initial x coordinate of the region (top-left).
        coord_y (int): Initial y coordinate of the region (top-left).
    """
    def __init__(self, coord_x, coord_y):
        self.coord_x = coord_x
        self.coord_y = coord_y

    def __str__(self):
        return "[{}, {}]".format(self.coord_x, self.coord_y)


    def __eq__(self, other):
        return self.coord_x == other.coord_x and self.coord_y == other.coord_y


    def to_array(self):
        """
        Convert to array

        Returns:
            tuple(int) - (coord_x, coord_y)
        """
        return self.coord_x, self.coord_y


    def distance(self, other):
        """
        Calculate distance to other coordinate
        """
        dx = self.coord_x - other.coord_x
        dy = self.coord_y - other.coord_y
        return int(_math.sqrt(dx**2 + dy**2))


    def find_closest(self, coords):
        """
        Find the closest coordiante to the specified list of coordinates.
        """
        coords = [coord.to_array() if isinstance(coord, _Coordinate) else coord for coord in coords]
        return _find_closest(coords, self.to_array())


class Region(_Coordinate):
    """
    Attributes:
        coord_x (int): Initial x coordinate of the region (top-left).
        coord_y (int): Initial y coordinate of the region (top-left).
        width (int): Width of the region.
        height (int): Height of the region.
    """
    def __init__(self, coord_x, coord_y, width, height):
        super().__init__(coord_x, coord_y)
        self.width = width
        self.height = height


    def __str__(self):
        return "[{}, {}:{}, {}]".format(self.coord_x, self.coord_y, self.width, self.height)


    def __eq__(self, other):
        if isinstance(other, Region):
            other = other.to_array()

        return self.coord_x == other[0] and \
                self.coord_y == other[1] and \
                self.width == other[2] and \
                self.height == other[3]


    @staticmethod
    def cast(coords):
        """
        Try convert coord to region
        """
        if isinstance(coords, Region):
            return coords

        if len(coords) >= 4:
            return Region(
                int(coords[0]),
                int(coords[1]),
                int(coords[2]),
                int(coords[3])
            )

        return None


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


    def inside(self, other):
        """
        Check this region is inside other region

        Args:
            other: array of int in order (coord_x, coord_y, width, height)

        Returns:
            boolean
        """
        if isinstance(other, Region):
            other = other.to_array()

        coord_x_min = other[0]
        coord_x_max = other[0] + other[2]
        coord_y_min = other[1]
        coord_y_max = other[1] + other[3]

        return coord_x_min <= self.coord_x and self.coord_x + self.width <= coord_x_max and \
               coord_y_min <= self.coord_y and self.coord_y + self.height <= coord_y_max


    def outside(self, other):
        """
        Check this region is outside other region

        Args:
            other: array of int in order (coord_x, coord_y, width, height)

        Returns:
            boolean
        """
        if isinstance(other, Region):
            other = other.to_array()

        coord_x_min = other[0]
        coord_x_max = other[0] + other[2]
        coord_y_min = other[1]
        coord_y_max = other[1] + other[3]

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
        return Location(self.coord_x, self.coord_y)


    def to_array(self):
        """
        Convert to array

        Returns:
            tuple(int) - (coord_x, coord_y, width, height)
        """
        return self.coord_x, self.coord_y, self.width, self.height


class Location(_Coordinate):
    """
    Attributes:
        coord_x (int): Initial x coordinate (top-left).
        coord_y (int): Initial y coordinate (top-left).
    """

    @staticmethod
    def cast(coords):
        """
        Try convert coord to location
        """
        if isinstance(coords, Location):
            return coords

        if len(coords) >= 2:
            return Location(int(coords[0]), int(coords[1]))
        return None

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


    def inside(self, region):
        """
        Check this location is inside other region

        Args:
            region: array of int in order (coord_x, coord_y, width, height)

        Returns:
            boolean
        """
        if isinstance(region, Region):
            region = region.to_array()

        coord_x_min = region[0]
        coord_x_max = region[0] + region[2]
        coord_y_min = region[1]
        coord_y_max = region[1] + region[3]

        return coord_x_min <= self.coord_x and self.coord_x <= coord_x_max and \
               coord_y_min <= self.coord_y and self.coord_y <= coord_y_max


    def outside(self, region):
        """
        Check this location is outside other region

        Args:
            region: array of int in order (coord_x, coord_y, width, height)

        Returns:
            boolean
        """
        if isinstance(region, Region):
            region = region.to_array()

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
        return Region.cast(coords)

    if len(coords) >= 2:
        return Location.cast(coords)

    return None


def _find_closest(coords, coord):
    """
    Utilizes a k-d tree to find the closest coordiante to the specified
    list of coordinates.

    Args:
        coords (array): Array of coordinates to search.
        coord (array): Array containing x and y of the coordinate.

    Returns:
        array: An array containing the distance of the closest coordinate
            in the list of coordinates to the specified coordinate as well the
            index of where it is in the list of coordinates
    """
    return spatial.KDTree(coords).query(coord)