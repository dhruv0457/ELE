"""Launch ELE CLI instantly"""
import sys
import os

if __name__ == "__main__":
    src_dir = os.path.join(os.path.dirname(__file__), "cli")
    sys.path.insert(0, src_dir)
    from src.app import main
    main()