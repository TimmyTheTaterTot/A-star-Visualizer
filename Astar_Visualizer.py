import pygame
import math
import random as rand
from Space import Space

white = (255, 255, 255)
black = (0, 0, 0)
off_white = (220, 220, 220)
green = (153, 255, 153)
blue = (128, 179, 255)
red = (255, 80, 80)
purple = (179, 102, 255)
dark_grey = (77, 77, 77)
light_grey = (217, 217, 217)

class App():
    def __init__(self, width, height):
        pygame.init()

        self.clock = pygame.time.Clock()

        self.a = None

        self.grid = [[Space(y, x) for x in range(width)] for y in range(height)]
        self.x_tiles = width
        self.y_tiles = height
        self.screenwidth = 707
        self.screenheight = 707
        self.tile_width = int((self.screenwidth + 2) / (self.x_tiles)) - 2
        self.tile_height = int((self.screenheight + 2) / (self.y_tiles)) - 2

        self.screenwidth = ((self.tile_width + 2) * self.x_tiles) + 2
        self.screenheight = ((self.tile_height + 2) * self.y_tiles) + 2

        self.start_tile = self.grid[0][0]
        self.end_tile = self.grid[self.x_tiles-1][self.y_tiles-1]
        self.path_spaces = []

        self.left_click = False
        self.middle_click = False
        self.right_click = False
        self.move_end_tile = True # True for end tile, False for start tile

        self.init_window()
        self.init_spaces()
        self.main_loop()


    def init_window(self):
        self.screen = pygame.display.set_mode((self.screenwidth, self.screenheight))
        pygame.display.set_caption("A* Pathfinding Visualizer")
        self.screen.fill(black)


    def init_spaces(self):
        for y in range(self.y_tiles):
            for x in range(self.x_tiles):
                App.draw_rect(self.grid[x][y], self.tile_width, self.tile_height)
                App.update_rect(self.grid[x][y], self.screen)

        self.start_tile.color = purple
        App.update_rect(self.start_tile, self.screen)


    @staticmethod
    def draw_rect(space: Space, width: int, height: int):
        x = (space.grid_x * (width + 2)) + 2
        y = (space.grid_y * (height + 2)) + 2
        space.x = x
        space.y = y
        space.rect = pygame.Rect(x, y, width, height)

        color = rand.randint(190, 230)
        space.basecolor = (color, color, color)
        space.color = (color, color, color)


    @staticmethod
    def update_rect(space: Space, screen: pygame.display):
            pygame.draw.rect(screen, space.color, space.rect)

    
    def find_route(self):
        to_search = [self.start_tile]
        searched = []
        self.start_tile.g = 0
        self.start_tile.h = App.get_distance(self.start_tile, self.end_tile)
        self.start_tile.f = self.start_tile.g + self.start_tile.h

        found_goal = False
        # find the current best tile to continue pathing from
        while len(to_search) > 0 and not found_goal:
            space = to_search[0]
            for unsearched in to_search:
                if unsearched.f < space.f or (unsearched.f == space.f and unsearched.h < space.h):
                    space = unsearched

            searched.append(space)
            to_search.remove(space)

            # if the space has a distance of 0 from the target space, then we have reached the target
            if space.h == 0:
                found_goal = True
                break

            # otherwise, check the surrounding squares and add them to the to_search list if they meet the proper criteria
            for i in range(3):
                for j in range(3):
                    if space.grid_x + i - 1 >= 0 and space.grid_x + i - 1 < self.x_tiles and space.grid_y + j - 1 >= 0 and space.grid_y + j - 1 < self.y_tiles: # check in bounds
                        new_space = self.grid[space.grid_x + i - 1][space.grid_y + j - 1]
                        if new_space.walkable and new_space not in searched: # make sure its not already been processed
                            if new_space not in to_search:
                                new_space.g = space.g + App.get_distance(space, new_space)
                                new_space.h = App.get_distance(new_space, self.end_tile)
                                new_space.f = new_space.g + new_space.h
                                new_space.previous = space
                                to_search.append(new_space)
                            elif (space.g + App.get_distance(space, new_space)) < new_space.g:
                                new_space.g = space.g + App.get_distance(space, new_space)
                                new_space.previous = space

        self.clear_path()
        if found_goal:
            self.backtrack(space)


    def clear_path(self):
        # reset previously colored in squares
        for space in self.path_spaces:
            if space.walkable:
                space.color = space.basecolor
            else:
                space.color = dark_grey
            App.update_rect(space, self.screen)
        self.path_spaces = []

    
    def backtrack(self, goal_space: Space):
        # backtrack through the spaces
        if goal_space.previous == None:
            return
        
        space = goal_space.previous
        while space.previous != None:
            self.path_spaces.append(space)
            space = space.previous

        # color the spaces blue
        for space in self.path_spaces:
            space.color = blue
            App.update_rect(space, self.screen)


    @staticmethod
    def get_distance(start_space: Space, end_space: Space):
        return math.sqrt(abs(end_space.grid_x - start_space.grid_x)**2 + abs(end_space.grid_y - start_space.grid_y)**2)

    
    def input_handler(self, event: pygame.event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # left click
                self.left_click = True
                self.update_selected(event.pos)
                self.find_route()
            elif event.button == 2: # middle click
                self.middle_click = True
                self.remove_wall(event.pos)
            elif event.button == 3: # right click
                self.right_click = True
                self.add_wall(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # left click released
                self.find_route()
                self.left_click = False
            elif event.button == 2: # middle click released
                self.middle_click = False
            elif event.button == 3: # right click released
                self.right_click = False

        elif event.type == pygame.MOUSEMOTION:
            if self.left_click or self.right_click or self.middle_click:
                if event.buttons[2] == 1: # right click held (takes priority over other clicks)
                    self.add_wall(event.pos)
                elif event.buttons[1] == 1: # middle click held
                    self.remove_wall(event.pos)
                elif event.buttons[0] == 1:
                    self.update_selected(event.pos)
                    self.find_route()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s: # s key
                self.move_end_tile = not self.move_end_tile


    def update_selected(self, pos):
        click_x, click_y = pos
        if click_x >= 0 and click_x < self.screenwidth - 2 and click_y >= 0 and click_y < self.screenheight - 2:
            if self.move_end_tile:
                if self.end_tile.walkable:
                    if self.end_tile is self.start_tile:
                        self.end_tile.color = purple
                    else:
                        self.end_tile.color = (self.end_tile.basecolor)
                else:
                    self.end_tile.color = dark_grey
                App.update_rect(self.end_tile, self.screen) # reset the previously selected space

                tile_x = int((click_x - 1) / (self.tile_width + 2))
                tile_y = int((click_y - 1)/ (self.tile_height + 2))
                self.end_tile = self.grid[tile_x][tile_y]
                self.end_tile.color = red
                App.update_rect(self.end_tile, self.screen) # highlight the newly selected space
            else:
                if self.start_tile.walkable:
                    if self.start_tile is self.end_tile:
                        self.start_tile.color = red
                    else:
                        self.start_tile.color = (self.start_tile.basecolor)
                else:
                    self.start_tile.color = dark_grey
                App.update_rect(self.start_tile, self.screen) # reset the previously selected space

                tile_x = int((click_x - 1) / (self.tile_width + 2))
                tile_y = int((click_y - 1)/ (self.tile_height + 2))
                self.start_tile = self.grid[tile_x][tile_y]
                self.start_tile.previous = None
                self.start_tile.color = purple
                App.update_rect(self.start_tile, self.screen) # highlight the newly selected space


    def add_wall(self, pos):
        self.clear_path()
        click_x, click_y = pos
        if click_x >= 0 and click_x < self.screenwidth - 2 and click_y >= 0 and click_y < self.screenheight - 2:
            tile_x = int((click_x - 1) / (self.tile_width + 2))
            tile_y = int((click_y - 1)/ (self.tile_height + 2))
            self.grid[tile_x][tile_y].color = dark_grey
            self.grid[tile_x][tile_y].walkable = False
            App.update_rect(self.grid[tile_x][tile_y], self.screen) # highlight the newly selected space

    
    def remove_wall(self, pos):
        click_x, click_y = pos
        if click_x >= 0 and click_x < self.screenwidth - 2 and click_y >= 0 and click_y < self.screenheight - 2:
            tile_x = int((click_x - 1) / (self.tile_width + 2))
            tile_y = int((click_y - 1)/ (self.tile_height + 2))
            space = self.grid[tile_x][tile_y]
            if not space.walkable: # only remove the wall if there is one there
                space.color = (space.basecolor)
                space.walkable = True
                App.update_rect(space, self.screen) # highlight the newly selected space


    def main_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.input_handler(event)

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    Application = App(20, 20)