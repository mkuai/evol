import time
from PIL import Image
import shutil
import glob
import random
import wda

tolerate = 30

pos_start = (1215, 1800)
pos_go = (1244, 1970)
pos_address = (750, 750)
pos_question1 = (700, 685)
pos_question2 = (700, 880)

RGBA_start = (236, 124, 152, 255)
RGBA_go = (134, 183, 227, 255)
RGBA_address = (230, 120, 145, 255)
RGBA_question1 = (231, 131, 153, 255)
RGBA_question2 = (234, 133, 155, 255)

click_positions = [(400, 800), (800, 800), (1200, 800)]
click_address = (787, 719)
click_questions = [(790, 728), (790, 928)]

board_width_question = 250
board_height_question = 96

c = wda.Client()
s = c.session()


class Strategy:
    def __init__(self):
        self.im = None
        self.im_pixel = None
        self.status = None
        # self.min_question_top = 2048
        # self.min_question_left = 1536
        self.question_center = None

    def load_image(self, im):
        self.im = im
        self.im_pixel = im.load()

    @staticmethod
    def check_match(rgba_std, rgba_new):
        for i in range(3):
            if rgba_std[i] - tolerate > rgba_new[i] or rgba_std[i] + tolerate < rgba_new[i]:
                return False
        return True

    def recognize_status(self):
        # questions
        if self.check_match(RGBA_question1, self.im_pixel[pos_question1]) and self.check_match(RGBA_question2,
                                                                            self.im_pixel[pos_question2]):
            self.status = 'question'
            return

        go = self.check_match(RGBA_go, self.im_pixel[pos_go])
        start = self.check_match(RGBA_start, self.im_pixel[pos_start])
        if start or go:
            add = self.recognize_address()
            if add:
                self.status = 'address'
            elif start:
                self.status = 'start'
            else:
                self.status = 'go'
        else:
            self.status = 'random'

    def recognize_address(self):
        w, h = self.im.size
        for i in range(int(h * 0.3), int(h * 0.5)):
            is_line = False
            start = 0
            for j in range(int(h * 0.3), int(h * 0.7)):
                if self.check_match(RGBA_address, self.im_pixel[j, i]):
                    if not is_line:
                        is_line = True
                        start = j
                else:
                    if is_line:
                        if (j - start) > board_width_question:
                            # self.min_question_top = min(self.min_question_top, i)
                            # self.min_question_left = min(self.min_question_left, start)
                            self.question_center = ((start + j) // 2, i + board_height_question // 2)
                            return True
                        is_line = False
        return False

    def get_taps(self):
        taps = []
        if self.status == 'question':
            taps.append(random.choice(click_questions))
        elif self.status == 'address':
            for _ in range(5):
                ran_pos = (self.question_center[0] + random.randint(-100, 100), self.question_center[1] + random.randint(-30, 30))
                taps.append(ran_pos)
        elif self.status == 'start':
            taps.append(pos_start)
        elif self.status == 'go':
            taps.append(pos_go)
        else:
            for _ in range(5):
                ran_pos = random.choice(click_positions)
                taps.append(ran_pos)
        return taps

    def get_sleep_time(self):
        if self.status == 'start':
            return 3
        elif self.status == 'go':
            return 3
        else:
            return None


def main():

    # for filename in glob.glob('add*.PNG'):
    #     print('-------------------------------')
    #     print(filename)
    #     im = Image.open(filename)
    #     # print(im.size, im.format, im.mode)
    #     print(recognize_status(im))
    strategy = Strategy()

    while True:
        print('-------------------------------')
        c.screenshot('screenshot.png')
        im = Image.open('screenshot.png')
        strategy.load_image(im)
        strategy.recognize_status()
        print(strategy.status)
        for tap_pos in strategy.get_taps():
            print(tap_pos)
            s.tap(tap_pos[0], tap_pos[1])
        sleep_time = strategy.get_sleep_time()
        if sleep_time:
            time.sleep(sleep_time)

        # shutil.copy('screenshot.png', 'images/{}.png'.format(int(time.time())))


if __name__ == '__main__':
    main()
