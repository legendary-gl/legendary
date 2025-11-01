import unittest
import os
from unittest.mock import patch
from legendary.lfs.wine_helpers import case_insensitive_file_search

class TestWineHelpers(unittest.TestCase):
    @patch('os.path.exists')
    def test_case_insensitive_file_search_nonexistent_dir(self, mock_exists):
        mock_exists.return_value = False
        result = case_insensitive_file_search('/nonexistent/path/to/file.txt')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
