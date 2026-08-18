import unittest
import os

DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(DIRECTORY, 'index.html')

class TestDriverTreeClickableRisks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            cls.html = f.read()

    def test_render_driver_tree_has_clickable_risk_buttons(self):
        """Verify Driver Tree renders interactive clickable buttons for linked risks and issues."""
        self.assertIn('filterByDriverTreeDeliverable', self.html, 'index.html must define filterByDriverTreeDeliverable')
        self.assertIn('onclick="filterByDriverTreeDeliverable', self.html)

    def test_filter_by_driver_tree_deliverable_function(self):
        """Verify filterByDriverTreeDeliverable handles both risks and issues tab transitions."""
        self.assertIn('function filterByDriverTreeDeliverable', self.html)
        self.assertIn("switchTab('overview')", self.html)
        self.assertIn("switchTab('issues')", self.html)

if __name__ == '__main__':
    unittest.main()
