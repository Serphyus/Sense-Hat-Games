import atexit
from time import sleep
from random import choice
from typing import Union, Tuple

from sense_hat import SenseHat


dir_move = {
    'up': [0, -1],
    'down': [0, 1],
    'left': [-1, 0],
    'right': [1, 0],
}

SNAKE_COLOR = (0, 100, 0)
APPLE_COLOR = (100, 0 ,0)

class Game:
    def __init__(self) -> None:
        self._sense = SenseHat()
        self._sense.clear()

        self._score = 0

        self._snake_body = [[3, 3]]
        self._stick_input = 'right'

        atexit.register(self._sense.clear)

    def end_screen(self, msg: str) -> None:
        self._sense.show_message(msg, text_colour=(100, 100, 100))
        exit()

    def create_apple(self) -> Union[Tuple[int, int], None]:
        pos_map = []
        for x in range(8):
            for y in range(8):
                pos_map.append([x, y])
        
        if len(pos_map) == len(self._snake_body):
            return

        apple_pos = choice([pos for pos in pos_map if pos not in self._snake_body])
        self._sense.set_pixel(*apple_pos, APPLE_COLOR)

        return apple_pos

    def snake_death(self) -> None:
        x, y = self._snake_body[-1]

        for _ in range(3):
            self._sense.set_pixel(x, y, (100, 100, 100))
            sleep(0.2)
            self._sense.set_pixel(x, y, SNAKE_COLOR)
            sleep(0.2)
        
        self.end_screen(str(self._score))

    def handle_input(self) -> dir:
        for event in self._sense.stick.get_events():
            if (new_input := event.direction) != 'middle':
                if len(self._snake_body) > 1:
                    if new_input == 'left' and self._stick_input == 'right': continue
                    if new_input == 'right' and self._stick_input == 'left': continue
                    if new_input == 'up' and self._stick_input == 'down': continue
                    if new_input == 'down' and self._stick_input == 'up': continue

                self._stick_input = event.direction

    def run(self) -> None:
        apple_pos = self.create_apple()
        
        while True:
            sleep(0.5)

            self.handle_input()

            x, y = self._snake_body[-1]

            d_x, d_y = dir_move[self._stick_input]
            new_pos = [x + d_x, y + d_y]

            if not all(p in range(8) for p in new_pos) or new_pos in self._snake_body[1:]:
                self.snake_death()
            
            self._snake_body.append(new_pos)

            if apple_pos == new_pos:
                self._score += 1

                apple_pos = self.create_apple()
                if apple_pos is None:
                    sleep(0.2)
                    self.end_screen('victory')
                
                self._sense.set_pixel(*apple_pos, APPLE_COLOR)
            
            else:
                self._sense.set_pixel(*self._snake_body[0], (0, 0, 0))
                self._snake_body.pop(0)
            
            self._sense.set_pixel(*self._snake_body[-1], SNAKE_COLOR)


if __name__ == '__main__':
    game = Game()
    game.run()