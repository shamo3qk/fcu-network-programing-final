import random


class BulletManager:
    def __init__(self, total_bullets, live_bullets):
        self.total_bullets = total_bullets
        self.live_bullets = live_bullets
        self.remaining_live_bullets = live_bullets
        self.bullet_chamber = [False] * total_bullets
        self.chamber_index = 0
        self.reload()

    def reload(self):
        self.chamber_index = 0
        self.remaining_live_bullets = self.live_bullets

        for i in range(self.total_bullets):
            if i < self.live_bullets:
                self.bullet_chamber[i] = True
            else:
                self.bullet_chamber[i] = False

        random.shuffle(self.bullet_chamber)

    def shoot(self):
        if not self.bullet_chamber[self.chamber_index]:
            self.chamber_index = (self.chamber_index + 1) % self.total_bullets
            return False

        self.chamber_index = (self.chamber_index + 1) % self.total_bullets
        self.remaining_live_bullets -= 1
        if self.remaining_live_bullets == 0:
            self.reload()

        return True
