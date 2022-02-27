import atexit
from time import sleep
from random import choice
from typing import Sequence, Tuple

from sense_hat import SenseHat


Cordinate = Tuple[int, int]
Shape = Sequence[Tuple[int, int]]
Color = Tuple[int, int, int]

rotation = {
    'up': 0,
    'down': 1
}

movement = {
    'left': -1,
    'right': 1
}

pieces = [
    [[[ 0, 1], [0, 0], [0, -1], [ 0, -2]], [0, 100, 100]],  # I piece
    [[[ 1, 0], [0, 0], [0, -1], [-1, -1]], [100, 0, 0]],    # S piece
    [[[-1, 0], [0, 0], [0, -1], [ 1, -1]], [0, 100, 0]],    # Z piece
    [[[ 1, 0], [0, 0], [0, -1], [ 1, -1]], [100, 100, 0]],  # O piece
    [[[-1, 0], [0, 0], [1,  0], [ 0, -1]], [100, 0, 100]],  # T piece
    [[[ 0, 1], [0, 0], [0, -1], [ 1, -1]], [150, 100, 0]],  # L piece
    [[[ 0, 1], [0, 0], [0, -1], [-1, -1]], [0, 0, 100]]     # J piece
]


class Piece:
    def __init__(self,
            center: Cordinate, 
            shape: Shape,
            color: Color
        ) -> None:

        self._center = center
        self._shape = shape
        self._color = color

    @property
    def center(self) -> Cordinate:
        return self._center

    @center.setter
    def center(self, center: Cordinate) -> None:
        self._center = center

    @property
    def pixels(self) -> Shape:
        pixels = []
        for (x, y) in self._shape:
            x += self._center[0]
            y += self._center[1]
            pixels.append([x, y])
        return pixels

    @property
    def color(self) -> Color:
        return self._color

    def get_rotated(self, direction: int, center_pos: bool = True) -> Shape:
        new_shape = []
        for (x, y) in self._shape:
            new_pos = [y, -x] if direction else [-y, x]
            if center_pos:
                new_pos[0] += self._center[0]
                new_pos[1] += self._center[1]
            new_shape.append(new_pos)
        return new_shape

    def rotate(self, direction: int) -> None:
        self._shape = self.get_rotated(direction, False)


class Game:
    def __init__(self) -> None:
        self._sense = SenseHat()
        self._sense.clear()

        self._field = [[None for _ in range(8)] for _ in range(8)]
        self.create_piece()        

        atexit.register(self._sense.clear)

    def game_over(self) -> None:
        self._sense.show_message('GAME OVER', text_colour=(100, 100, 100))
        exit()

    def create_piece(self) -> None:
        self._piece = Piece([3, -1], *choice(pieces))
        self.reset_fall_counter()
        self.render_piece()

    def clear_piece(self) -> None:
        self.render_piece((0, 0, 0))

    def render_piece(self, color: Color = None) -> None:
        if color is None:
            color = self._piece.color

        for pixel in self._piece.pixels:
            if all(n in range(8) for n in pixel):
                self._sense.set_pixel(*pixel, color)

    def reset_fall_counter(self) -> None:
        self._fall_counter = 20

    def get_full_lines(self) -> list:
        return [i for i, l in enumerate(self._field) if all(l)]
                
    def clear_lines(self, lines: Sequence[int]) -> None:
        for line_num in lines:
            self._field.pop(line_num)
            new_line = [None for _ in range(8)]
            self._field.insert(0, new_line)
        
        blink_pixel_map_1 = self._sense.get_pixels()
        blink_pixel_map_2 = self._sense.get_pixels()
        
        for line_num in lines:
            for x in range(8):
                blink_pixel_map_1[8*line_num + x] = [100, 100, 100]
        
        for _ in range(3):
            self._sense.set_pixels(blink_pixel_map_1)
            sleep(0.2)
            self._sense.set_pixels(blink_pixel_map_2)
            sleep(0.2)

        for y, row in enumerate(self._field):
            for x, color in enumerate(row):
                if color is None:
                    color = (0, 0, 0)
                self._sense.set_pixel(x, y, color)

    def store_piece(self) -> None:
        for (x, y) in self._piece.pixels:
            if y < 0:
                self.game_over()
            self._field[y][x] = self._piece.color

    def move_down(self) -> None:
        for (x, y) in self._piece.pixels:
            if y == 7 or self._field[abs(y+1)][x] is not None:
                if y < 0:
                    self.game_over()
                
                self.store_piece()
                if (completed := self.get_full_lines()):
                    self.clear_lines(completed)
                self.create_piece()
                
                return

        self.clear_piece()
        self._piece.center[1] += 1
        self.render_piece()

        self.reset_fall_counter()

    def move_piece(self, direction: str) -> None:
        if direction in movement:
            move = movement[direction]
            for (x, y) in self._piece.pixels:
                x += move
                if x not in range(8):
                    return
                elif y > 0 and self._field[y][x] is not None:
                    return
                
            self.clear_piece()
            self._piece.center[0] += move
            self.render_piece()
        
        elif direction in rotation:
            rotate_dir = rotation[direction]
            for (x, y) in self._piece.get_rotated(rotate_dir):
                if x not in range(8) or self._field[y][x] is not None:
                    return
            
            self.clear_piece()
            self._piece.rotate(rotate_dir)
            self.render_piece()

    def run(self):
        while True:
            sleep(0.05)
            
            for event in self._sense.stick.get_events():
                if event.action in ['pressed', 'held']:
                    direction = event.direction
                    if direction == 'middle':
                        self.move_down()
                    else:
                        self.move_piece(direction)

            self._fall_counter -= 1
            if not self._fall_counter:
                self.move_down()


if __name__ == '__main__':
    game = Game()
    game.run()