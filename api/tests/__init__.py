import sys
import os

print('HERE', flush=True)

# Add the directory above 'tests' to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../api')
    )
)
