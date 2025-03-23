import pygame
import heapq

class Agent(pygame.sprite.Sprite):
    def __init__(self, environment, grid_size):
        super().__init__()
        self.image = pygame.Surface((grid_size, grid_size))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.grid_size = grid_size
        self.environment = environment
        self.position = [0, 0]
        self.rect.topleft = (0, 0)
        self.task_completed = 0
        self.completed_tasks = []
        self.path = []
        self.moving = False
        self.total_path_cost =  0
    def move(self):
        if self.path:
            next_position = self.path.pop(0)
            self.position = list(next_position)
            self.rect.topleft = (self.position[0] * self.grid_size, self.position[1] * self.grid_size)
            self.total_path_cost += 1
            self.check_task_completion()
        else:
            self.moving = False

    def check_task_completion(self):
        position_tuple = tuple(self.position)
        if position_tuple in self.environment.task_locations:
            task_number = self.environment.task_locations.pop(position_tuple)
            self.task_completed += 1
            self.completed_tasks.append(task_number)

    def find_nearest_task(self):
        nearest_task = None
        shortest_path = None
        for task_position in self.environment.task_locations.keys():
            path = self.find_path_to(task_position)
            if path:
                if not shortest_path or len(path) < len(shortest_path):
                    shortest_path = path
                    nearest_task = task_position
        if shortest_path:
            self.path = shortest_path[1:]
            self.moving = True

    def find_path_to(self, target):
        start = tuple(self.position)
        goal = target
        threshold = self.heuristic(start, goal)

        while True:
            result, path, new_threshold = self.ida_star_search(start, goal, 0, threshold, [start])
            if result:
                return path
            if new_threshold == float('inf'):
                return None
            threshold = new_threshold

    def ida_star_search(self, current, goal, g_score, threshold, path):
        f_score = g_score + self.heuristic(current, goal)
        if f_score > threshold:
            return False, None, f_score
        if current == goal:
            return True, path, threshold

        min_threshold = float('inf')
        for neighbor in self.get_neighbors(*current):
            if neighbor not in path:
                result, new_path, new_threshold = self.ida_star_search(
                    neighbor, goal, g_score + 1, threshold, path + [neighbor]
                )
                if result:
                    return True, new_path, threshold
                min_threshold = min(min_threshold, new_threshold)

        return False, None, min_threshold

    def heuristic(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def get_neighbors(self, x, y):
        neighbors = []
        directions = [("up", (0, -1)), ("down", (0, 1)), ("left", (-1, 0)), ("right", (1, 0))]
        for _, (dx, dy) in directions:
            nx, ny = x + dx, y + dy
            if self.environment.is_within_bounds(nx, ny) and not self.environment.is_barrier(nx, ny):
                neighbors.append((nx, ny))
        return neighbors