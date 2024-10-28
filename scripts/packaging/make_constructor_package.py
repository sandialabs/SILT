"""Make Constructor packages for distribution.

Usage:
    make_constructor_package.py [-L,--log-level=LOG_LEVEL] [-O,--output-directory=OUTPUT_DIR]

Options:
    -L, --log-level=LOG_LEVEL            Set logging level to LOG_LEVEL [default: INFO]
    -O, --output-directory=OUTPUT_DIR    Set output directory to OUTPUT_DIR [default: pkg-output]
"""

import os
import re
from pathlib import Path
import argparse
import subprocess


script_dir: Path = Path(__file__).parent.resolve()
template_dir: Path = script_dir / "templates"
construct_template = template_dir / "construct_template.yaml"
PYPROJECT_TOML_FILE = script_dir /  '..' / '..' / 'silt' / 'pyproject.toml'

class tmp_change_dir:
    """Context manager for temporarily changing the working directory."""

    def __init__(self, new_path: Path):
        """tmp_change_dir

        Parameters
        ----------
        new_path : Path
            New path to switch to
        """
        self._new_path: Path = new_path.resolve()
        self._old_path = None

    def __enter__(self):
        """Switches to new directory.
        """
        self._old_path = Path.cwd()
        os.chdir(self._new_path)

    def __exit__(
        self,
        exc_type,   # Optional[type],
        exc_value,  # Optional[Exception],
        traceback   # Optional[TracebackType],
    ):
        """Switches to old directory.
        """
        os.chdir(self._old_path)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-O', '--output-directory', default='')
    parser.add_argument('-L', '--log-level', default='INFO')
    args = parser.parse_args()
    return args


def parse_version_from_file(file_path):
    # Read the file and filter out the metadata lines

    with open(file_path, 'r') as file:
        content = file.read()

    pattern = re.compile(r'version\s*=\s*["\']([^"\']+)["\']')

    pattern_match = pattern.search(content)

    if pattern_match:
        return pattern_match.group(1)
    else:
        raise ValueError("Version number not found in the file.")


def main(args=None):
    args = parse_args(args)
    output_dir: Path = Path(args.output_directory).resolve()
    if not output_dir.exists():
        output_dir.mkdir()

    silt_version = parse_version_from_file(PYPROJECT_TOML_FILE)

    # make substitutions
    with open(construct_template, 'r') as in_file:
        text = in_file.read()
        with open(template_dir / "construct.yaml", "w") as out_file:
            text = re.sub(r'{{.*full_version.*}}', silt_version, text)
            out_file.write(text)

    cmd = ["constructor", "."]
    if args.output_directory:
        cmd += ["--output-dir", output_dir]

    print("Running ", cmd)
    with tmp_change_dir(template_dir):
        subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
