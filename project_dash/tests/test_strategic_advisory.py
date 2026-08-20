import unittest
import os

DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(DIRECTORY, 'index.html')

class TestStrategicAdvisory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            cls.html = f.read()

    def test_google_need_to_know_global_banner(self):
        """Verify Google Need to Know (NTK) classification badge is in the title banner."""
        self.assertIn('id="ntkClassificationBadge"', self.html)
        self.assertIn('Google Need to Know (NTK)', self.html)

    def test_looking_around_corner_module(self):
        """Verify Looking Around the Corner module is present in Executive Summary."""
        self.assertIn('id="lookingAroundCornerSection"', self.html)
        self.assertIn('Looking Around the Corner', self.html)
        self.assertIn('renderLookingAroundCorner', self.html)

if __name__ == '__main__':
    unittest.main()
