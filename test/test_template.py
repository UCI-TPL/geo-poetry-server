import sys
import os
# Add the parent directory (one level above test/) to the import search path
parent_dir = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.append(parent_dir)

##############
# Put tests and all other needed code here
##############

if __name__ == '__main__':
	import pytest
	# Run pytest on this file
	pytest.main([__file__])