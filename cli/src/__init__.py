"""ELE CLI package — lazy imports only"""

def main():
    from .app import main as _main
    _main()

__all__ = ["main"]