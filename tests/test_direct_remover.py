import unittest
import shutil
from pathlib import Path
from unittest.mock import patch
from remover.direct_delete import DirectRemover

class TestDirectRemover(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_artifacts_unit")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.file1 = self.test_dir / "file1.txt"
        self.file1.touch()
        self.dir1 = self.test_dir / "dir1"
        self.dir1.mkdir()
        self.remover = DirectRemover()

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_remove_all_confirmed(self):
        artifacts = [self.file1, self.dir1]
        with patch('builtins.input', side_effect=['y', 'y']):
            with patch('builtins.print'):  # Silence output during tests
                result = self.remover.remove(artifacts)
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.removed), 2)
        self.assertIn(self.file1, result.removed)
        self.assertIn(self.dir1, result.removed)
        self.assertFalse(self.file1.exists())
        self.assertFalse(self.dir1.exists())

    def test_remove_none_confirmed(self):
        artifacts = [self.file1, self.dir1]
        with patch('builtins.input', side_effect=['n', 'n']):
            with patch('builtins.print'):
                result = self.remover.remove(artifacts)
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.removed), 0)
        self.assertEqual(len(result.skipped), 2)
        self.assertTrue(self.file1.exists())
        self.assertTrue(self.dir1.exists())

    def test_remove_partial_confirmed(self):
        artifacts = [self.file1, self.dir1]
        with patch('builtins.input', side_effect=['y', 'n']):
            with patch('builtins.print'):
                result = self.remover.remove(artifacts)
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.removed), 1)
        self.assertEqual(len(result.skipped), 1)
        self.assertIn(self.file1, result.removed)
        self.assertIn(self.dir1, result.skipped)
        self.assertFalse(self.file1.exists())
        self.assertTrue(self.dir1.exists())

    def test_remove_interrupted(self):
        artifacts = [self.file1, self.dir1]
        with patch('builtins.input', side_effect=EOFError):
            with patch('builtins.print'):
                result = self.remover.remove(artifacts)
        
        self.assertFalse(result.success)
        # Should stop after first attempt and not delete anything
        self.assertTrue(self.file1.exists())
        self.assertTrue(self.dir1.exists())

    def test_remove_error(self):
        artifacts = [self.file1]
        # Simulate error by patching unlink to raise OSError
        with patch('builtins.input', side_effect=['y']):
            with patch('pathlib.Path.unlink', side_effect=OSError("Permission denied")):
                with patch('builtins.print'):
                    result = self.remover.remove(artifacts)
        
        self.assertFalse(result.success)
        self.assertIn(self.file1, result.failed)
        self.assertTrue(self.file1.exists())

if __name__ == '__main__':
    unittest.main()
