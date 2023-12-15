import os
import tempfile
from gpt_engineer.cli.file_selector import TerminalFileSelector

def test_find_in_files():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some files in the directory
        file1 = os.path.join(tmpdir, 'file1.txt')
        with open(file1, 'w') as f:
            f.write('This is a test file with the word "apple".')
        
        file2 = os.path.join(tmpdir, 'file2.txt')
        with open(file2, 'w') as f:
            f.write('This is another test file with the word "banana".')
        
        file3 = os.path.join(tmpdir, 'file3.txt')
        with open(file3, 'w') as f:
            f.write('This is a test file with the word "apple" and "banana".')
        
        # Create a TerminalFileSelector instance
        file_selector = TerminalFileSelector(tmpdir)
        
        # Search for the word "apple"
        result = file_selector.find_in_files('apple')
        
        # Check that the correct files are returned
        assert set(result) == set([file1, file3])