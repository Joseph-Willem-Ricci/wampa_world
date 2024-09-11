import unittest
import pycodestyle

from gradescope_utils.autograder_utils.decorators import weight
from gradescope_utils.autograder_utils.files import check_submitted_files


class TestFiles(unittest.TestCase):
    @weight(0)
    def test_submitted_files(self):
        missing_files = check_submitted_files(['agent.py'], base='')
        for path in missing_files:
            print('Missing %s' % path)
        self.assertEqual(len(missing_files), 0, 'Missing some required files!')
        print('All required files submitted!')

    @weight(5)
    def test_style(self):
        """Test that we conform to PEP-8 style standards."""
        style = pycodestyle.StyleGuide()
        result = style.check_files(['agent.py', 'wampa_world.py'])
        self.assertEqual(result.total_errors, 0,
                         "Please fix the above style errors/warnings and resubmit.")