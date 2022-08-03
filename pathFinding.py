import sys
import time

import pygame

# import os
# try:
#     os.environ["DISPLAY"]
# except:
#     os.environ["SDL_VIDEODRIVER"] = "dummy"

delay = 0.4

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

pygame.init()
window_width = 500
window_height = 500
screen = None

resolution_x = 20
resolution_y = 20

box_width = window_width // resolution_x
box_height = window_height // resolution_y

window = pygame.display.set_mode((window_width, window_height + 200))

array_box = []

font = pygame.font.SysFont("chalkduster.ttf", 24)


def clamp(number, minNumber, maxNumber):
    return max(minNumber, min(number, maxNumber))


class Box:
    def __init__(self, i, j):
        self.x = i
        self.y = j
        self.width = box_width - 2
        self.height = box_height - 2
        self.is_wall = False
        self.is_start = False
        self.is_target = False
        self.parent = None
        self.neighbors = []
        # Total cost of the node
        self.f = 0
        # Is the distance between the current node and the start node
        self.g = 0
        # Is The heuristic -- estimated from the current node to the end node
        self.h = 0

    def draw(self, win, color):
        x = self.x * box_width
        y = self.y * box_height
        pygame.draw.rect(win, color, (x, y, self.width, self.height))

    def calculate(self, box, target):
        self.g = box.g + 1
        h_x = pow(abs(target.x - self.x), 2)
        h_y = pow(abs(target.y - self.y), 2)
        self.h = h_x + h_y
        self.f = self.g + self.h
        self.parent = box

    def isEqual(self, target):
        return self.x == target.x and self.y == target.y

    def set_neighbors(self):
        neighbors = []
        for i in range(-1, 2):
            neighbor_x = self.x + i
            for j in range(-1, 2):
                neighbor_y = self.y + j
                if (
                    neighbor_x >= 0
                    and neighbor_y >= 0
                    and neighbor_x < 20
                    and neighbor_y < 20
                    and not (neighbor_x == self.x and neighbor_y == self.y)
                ):
                    neighbors.append(array_box[neighbor_x][neighbor_y])
        self.neighbors = neighbors
        return neighbors


class AStar:
    def __init__(self, start):
        self.start_node = start
        self.target_node = None
        self.open_list = [start_node]
        self.closed_list = []
        self.path = []
        self.finding = False

    def get_lowest_f_cost_open_list(self):
        lowest = None
        for node in self.open_list:
            if lowest is None or lowest.f > node.f:
                lowest = node
        return lowest

    def remove_node_open_list(self, node):
        for n in self.open_list:
            if n.x == node.x and n.y == node.y:
                self.open_list.remove(n)

    def get_neighbor_open_list(self, node):
        for n in self.open_list:
            if n.x == node.x and n.y == node.y:
                return n

    def calculate(self, current_node):
        if current_node.isEqual(self.target_node):
            self.construct_path(self.target_node)
            self.finding = False
        if self.target_node is None:
            return
        neighbors = current_node.neighbors
        for neighbor in neighbors:
            if neighbor.is_wall is True:
                continue
            if neighbor in self.closed_list:
                continue
            neighbor.calculate(current_node, self.target_node)
            if neighbor not in self.open_list:
                self.open_list.append(neighbor)
            else:
                open_neighbor = self.get_neighbor_open_list(neighbor)
                if open_neighbor is not None and neighbor.g < open_neighbor.g:
                    open_neighbor.g = neighbor.g
                    open_neighbor.parent = neighbor.parent

    def construct_path(self, node):
        self.path = [node]
        while node.parent is not None:
            node = node.parent
            self.path.append(node)
        return self.path


def find_box_by_mouse_pos(mouse_pos):
    mouse_pos = pygame.mouse.get_pos()
    i = int((mouse_pos[0] / window_width) * resolution_x)
    j = int((mouse_pos[1] / window_height) * resolution_y)
    clamp_i = clamp(i, 0, resolution_x - 1)
    clamp_j = clamp(j, 0, resolution_y - 1)
    return array_box[clamp_i][clamp_j]


# Initialize box
for i in range(resolution_x):
    array = []
    for j in range(resolution_y):
        array.append(Box(i, j))
    array_box.append(array)
# Set neighbors for box in array
for i in range(0, resolution_x - 1):
    for j in range(0, resolution_y - 1):
        array_box[i][j].set_neighbors()

# Set start position
array_box[0][0].is_start = True
start_node = array_box[0][0]
a_star = AStar(start_node)


def main():
    while True:
        window.fill((000, 000, 000))

        for i in range(resolution_x):
            for j in range(resolution_y):
                box = array_box[i][j]
                color = (90, 90, 90)
                if box.is_start:
                    color = (200, 200, 0)
                elif box.is_wall:
                    color = (150, 150, 150)
                elif box.is_target:
                    color = (0, 200, 200)
                box.draw(window, color)

        for event in pygame.event.get():
            mouse_pos = pygame.mouse.get_pos()
            box = find_box_by_mouse_pos(mouse_pos)
            # Quit window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Mouse button Down
            if event.type == pygame.MOUSEMOTION:
                if event.buttons[0] == 1:
                    box.is_target = False
                    box.is_wall = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    box.is_target = False
                    box.is_wall = True
                if event.button == 3:
                    if a_star.target_node is None:
                        a_star.target_node = box
                        box.is_wall = False
                        box.is_target = True
                    else:
                        a_star.finding = True
                        while len(a_star.open_list) > 0 and a_star.finding is True:
                            node_lowest_cost = a_star.get_lowest_f_cost_open_list()
                            a_star.remove_node_open_list(node_lowest_cost)
                            a_star.closed_list.append(node_lowest_cost)
                            a_star.calculate(node_lowest_cost)

        # Debug
        # Highlight open_list
        for open in a_star.open_list:
            if open.isEqual(a_star.start_node):
                continue
            if a_star.target_node is not None and open.isEqual(a_star.target_node):
                continue
            open.draw(window, GREEN)
        # Highlight ClosedList
        for closed in a_star.closed_list:
            if closed.isEqual(a_star.start_node):
                continue
            if a_star.target_node is not None and closed.isEqual(a_star.target_node):
                continue
            closed.draw(window, RED)

        # Get Box Hovered
        box = find_box_by_mouse_pos(pygame.mouse.get_pos())
        box.draw(window, GRAY)
        neighbors = box.neighbors

        img = font.render(
            f"Total Neighbor:{len(neighbors)} \
            F: {box.f} G: {box.g} H: {box.h}",
            True,
            GRAY,
        )
        img2 = font.render(
            f"Closed List:{len(a_star.closed_list)} \
            Open List: {len(a_star.open_list)}",
            True,
            GRAY,
        )
        window.blit(img, (20, window_height + 7))
        window.blit(img2, (20, window_height + 27))

        for path in a_star.path:
            path.draw(window, (255, 255, 255))

        # pygame.display.update()
        pygame.display.flip()
        # time.sleep(delay)


main()
