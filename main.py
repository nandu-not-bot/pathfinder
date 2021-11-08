import random
from time import sleep
import pygame

pygame.init()

END = 0
START = 1
WALL = 2
UNEXPLORED = 3
OPENED = 4
CLOSED = 5
PATH = 6

# G cost = distance from start
# H cost = distance from end
# F cost = G + H


class Node:
    def __init__(self, type_, g=0, h=0, path=[]):
        """G cost = distance from start
        H cost = distance from end
        F cost = G + H
        """
        self.g = g
        self.h = h
        self.f = self.g + self.h
        self.type = type_
        self.path: list = path

    def __repr__(self) -> str:
        return f"g={self.g}, h={self.h}, f={self.f}"


class Pathfinder:
    def __init__(self, w=650, h=650):
        self.display = pygame.display
        self.w = w
        self.h = h
        self.NODE_SIZE = 50
        self.border = 5
        self.time = .05

        self.screen = self.display.set_mode([self.w, self.h])

        self.nodes: list[list[Node]] = [
            [Node(UNEXPLORED) for _ in range(self.w // self.NODE_SIZE)]
            for _ in range(self.h // self.NODE_SIZE)
        ]

        self.start_coord = (0, 0)
        self.end_coord = (10, 0)

        self.nodes[self.start_coord[1]][self.start_coord[0]] = Node(
            START, h=self._get_h(*self.start_coord)
        )
        self.nodes[self.end_coord[1]][self.end_coord[0]] = Node(
            END, self._get_g(*self.end_coord)
        )

        self.open_nodes = []

        self.edit_mode_active = True
        self.first_step_taken = False
        self.end_node_found = False
        self.set_start = True

        self.right_click_dragging = False
        self.left_click_dragging = False

        self.auto_mode = False

    def run(self):
        self.running = True
        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    self._key_press(event)

                if self.edit_mode_active:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # left click
                            self.left_click_dragging = True
                            self._left_click()
                        elif event.button == 2:
                            self._middle_click()
                        elif event.button == 3:  # right click
                            self.right_click_dragging = True
                            self._right_click()

                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.right_click_dragging = False
                        self.left_click_dragging = False

                    elif event.type == pygame.MOUSEMOTION:
                        if self.right_click_dragging:
                            self._right_click()
                        elif self.left_click_dragging:
                            self._left_click()

            if self.auto_mode and not self.end_node_found:
                self._step_pf()
                sleep(self.time)

            self._update_screen()

    def _key_press(self, event):
        if (
            event.key == pygame.K_SPACE
            and not self.end_node_found
            and not self.auto_mode
        ):
            if self.edit_mode_active:
                self.edit_mode_active = False
            self._step_pf()

        elif event.key == pygame.K_RETURN:
            if not self.auto_mode:
                self.auto_mode = True

        if event.key == pygame.K_r:
            self._reset()

        if event.key == pygame.K_c:
            self._clear()

    def _reset(self):
        for y, row in enumerate(self.nodes):
            for x, node in enumerate(row):
                if node.type not in {WALL, START, END}:
                    self.nodes[y][x] = Node(UNEXPLORED)

        self._reset_bools()

    def _clear(self):
        for y, row in enumerate(self.nodes):
            for x, node in enumerate(row):
                if node.type not in {START, END}:
                    self.nodes[y][x] = Node(UNEXPLORED)

        self._reset_bools()

    def _reset_bools(self):
        self.open_nodes = []
        self.edit_mode_active = True
        self.first_step_taken = False
        self.end_node_found = False
        self.set_start = True
        self.auto_mode = False

    def _gen_rect_coords(self, x, y):
        return [
            i * self.NODE_SIZE for i in [x, y, x + self.NODE_SIZE, y + self.NODE_SIZE]
        ]

    @staticmethod
    def _get_dist(x1, x2, y1, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def _get_g(self, x, y):
        return self._get_dist(x, self.start_coord[0], y, self.start_coord[1])

    def _get_h(self, x, y):
        return self._get_dist(x, self.end_coord[0], y, self.end_coord[1])

    def _step_pf(self):
        if not self.first_step_taken:
            self._update_surrounding(self.start_coord)
            self.first_step_taken = True
        else:
            m = [
                node
                for node in self.open_nodes
                if self.nodes[node[1]][node[0]].f == self._get_lowest_f()
            ]

            m.sort(key=lambda coord: self.nodes[coord[1]][coord[0]].h)

            self._update_surrounding(m[0])

        self._update_open_node_set()

    def _get_lowest_f(self) -> int:
        m = 0
        for x, y in self.open_nodes:
            if self.nodes[y][x].f <= m or m == 0:
                m = self.nodes[y][x].f

        return m

    def _update_open_node_set(self):
        self.open_nodes = []
        for y, row in enumerate(self.nodes):
            for x, node in enumerate(row):
                if node.type == OPENED:
                    self.open_nodes.append((x, y))

    def _update_surrounding(self, node_to_check):
        main_x, main_y = node_to_check

        if (main := self.nodes[main_y][main_x]).type == OPENED:
            self.nodes[main_y][main_x] = Node(
                CLOSED, self._get_g(main_x, main_y), self._get_h(main_x, main_y)
            )

        adj = self._get_adj(main_x, main_y)

        for x, y in adj:
            node = self.nodes[y][x]
            if node.type == END:
                self.end_node_found = True
                main.path += [(main_x, main_y)]
                self._show_path(main)
            elif node.type in {UNEXPLORED, OPENED}:
                future = Node(
                    OPENED,
                    self._get_dist(x, main_x, y, main_y) + main.g,
                    self._get_h(x, y),
                    main.path + [(main_x, main_y)],
                )
                if node.type == UNEXPLORED or node.f > future.f:
                    self.nodes[y][x] = Node(
                        OPENED,
                        self._get_dist(x, main_x, y, main_y) + main.g,
                        self._get_h(x, y),
                        main.path + [(main_x, main_y)],
                    )

    def _show_path(self, node: Node):
        for x, y in node.path[-1:0:-1]:
            self.nodes[y][x] = Node(PATH)
            self._update_screen()
            sleep(self.time)

    def _get_adj(self, x, y) -> "set[tuple[int]]":
        board_size = self.w // self.NODE_SIZE

        adj = set()

        for i in range(-1, 2):
            for j in range(-1, 2):
                if (
                    board_size > y + i >= 0
                    and board_size > x + j >= 0
                    and not (i == j == 0)
                    and self.nodes[y + i][x + j].type in {UNEXPLORED, END, OPENED}
                ):
                    adj.add((x + j, y + i))

        return adj

    def _left_click(self):
        pos = pygame.mouse.get_pos()
        x, y = pos[0] // self.NODE_SIZE, pos[1] // self.NODE_SIZE
        node = self.nodes[y][x]

        if node.type == UNEXPLORED:
            self.nodes[y][x] = Node(WALL)

        self._update_screen()

    def _right_click(self):
        pos = pygame.mouse.get_pos()
        x, y = pos[0] // self.NODE_SIZE, pos[1] // self.NODE_SIZE
        node = self.nodes[y][x]

        if node.type == WALL:
            self.nodes[y][x] = Node(UNEXPLORED)

        self._update_screen()

    def _middle_click(self):
        pos = pygame.mouse.get_pos()
        x, y = pos[0] // self.NODE_SIZE, pos[1] // self.NODE_SIZE
        node = self.nodes[y][x]

        if self.set_start and node.type not in {START, END}:
            self.nodes[self.start_coord[1]][self.start_coord[0]] = Node(UNEXPLORED)
            self.set_start = False
            self.start_coord = x, y
            self.nodes[y][x] = Node(START, h=self._get_h(x, y))
        elif not self.set_start and node.type not in {START, END}:
            self.nodes[self.end_coord[1]][self.end_coord[0]] = Node(UNEXPLORED)
            self.set_start = True
            self.end_coord = x, y
            self.nodes[y][x] = Node(END, self._get_g(x, y))

    def _update_screen(self):
        self.display.flip()

        color = 0xFFFFFF

        for y, row in enumerate(self.nodes):
            for x, node in enumerate(row):
                if node.type == UNEXPLORED:
                    color = 0xFFFFFF  # White
                elif node.type == START:
                    color = 0x0000FF  # Blue
                elif node.type == END:
                    color = 0xC678DD  # Lavender
                elif node.type == WALL:
                    color = 0x000000  # Black
                elif node.type == OPENED:
                    color = 0x00FF00  # Green
                elif node.type == CLOSED:
                    color = 0xFF0000  # Red
                elif node.type == PATH:
                    color = 0xFFFF00  # Yellow

                border_coords = x1, y1, x2, y2 = self._gen_rect_coords(x, y)
                rect_coords = x1 + self.border, y1 + self.border, x2 - self.border, y2 - self.border

                pygame.draw.rect(self.screen, 0x000000, border_coords)
                pygame.draw.rect(self.screen, color, rect_coords)


if __name__ == "__main__":
    pf = Pathfinder()
    out = pf.run()

