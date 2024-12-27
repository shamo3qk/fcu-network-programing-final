import unittest
from src.bullet_manager import BulletManager


class TestBulletManager(unittest.TestCase):
    def test_init_success(self):
        bullet_manager = BulletManager(7, 2)

        self.assertEqual(bullet_manager.total_bullets, 7)
        self.assertEqual(bullet_manager.live_bullets, 2)
        self.assertEqual(bullet_manager.remaining_live_bullets, 2)
        self.assertNotEqual(
            bullet_manager.bullet_chamber, [False] * bullet_manager.total_bullets
        )
        self.assertEqual(bullet_manager.chamber_index, 0)

    def test_shoot_once(self):
        bullet_manager = BulletManager(7, 2)

        result = bullet_manager.shoot()
        if result:
            self.assertEqual(bullet_manager.remaining_live_bullets, 1)
        else:
            self.assertEqual(bullet_manager.remaining_live_bullets, 2)

        self.assertEqual(bullet_manager.chamber_index, 1)

    def test_shoot_until_live_bullet_out(self):
        bullet_manager = BulletManager(7, 2)

        hit_count = 0
        while hit_count < bullet_manager.live_bullets:
            if bullet_manager.shoot():
                hit_count += 1

        self.assertEqual(bullet_manager.remaining_live_bullets, 2)
        self.assertEqual(bullet_manager.chamber_index, 0)


if __name__ == "__main__":
    unittest.main()
