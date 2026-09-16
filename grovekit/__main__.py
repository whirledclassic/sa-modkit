from __future__ import print_function
import sys

def main():
    if len(sys.argv) > 1:
        from grovekit.cli import main as cli_main
        return cli_main(sys.argv[1:])
    try:
        from grovekit.app import main as gui_main
        gui_main()
        return 0
    except SystemExit:
        raise
    except Exception:
        from grovekit.cli import main as cli_main
        return cli_main(["--browse"])

if __name__ == "__main__":
    sys.exit(main() or 0)
