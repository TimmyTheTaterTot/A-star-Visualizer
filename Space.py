class Space():
    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.x = None
        self.y = None
        self.rect = None
        self.basecolor = None
        self.color = None
        self.walkable = True
        self.g = None # distance from start point
        self.h = None # distance from goal
        self.f = None # total distance. The space's "route score"
        self.previous = None # a reference to the previous space for backtracking purposes