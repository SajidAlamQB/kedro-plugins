import os
import sys
import re
import requests
from pathlib import Path

VERSION_MATCHSTR = r'\s*__version__\s*=\s*"(\d+\.\d+\.\d+)"'


def get_package_version(base_path, package_path):
    init_file_path = Path(base_path) / package_path / "__init__.py"
    match_obj = re.search(VERSION_MATCHSTR, Path(init_file_path).read_text())
    return match_obj.group(1)


def check_no_version_pypi(pypi_endpoint, package_name, package_version):
    print(f"Check if {package_name} {package_version} is on pypi")
    response = requests.get(pypi_endpoint, timeout=10)
    if response.status_code == 404:
        # Not exist on Pypi - do release
        print(f"Starting the release of {package_name} {package_version}")
        return True
    else:
        print(f"Skipped: {package_name} {package_version} already exists on PyPI")
        return False


if __name__ == "__main__":
    """Check if a package needs to be released"""
    if len(sys.argv) != 2:
        print("Please provide package path as an argument.")
        sys.exit(1)

    env_file = os.getenv('GITHUB_ENV')

    package_path = sys.argv[1]
    package_name, _ = package_path.split("/")

    base_path = Path()
    package_version = get_package_version(base_path, package_path)
    pypi_endpoint = f"https://pypi.org/pypi/{package_name}/{package_version}/json/"

    print(package_name, package_version)
    if check_no_version_pypi(pypi_endpoint, package_name, package_version):
        print(f"New release needed for {package_name} {package_version}")
        with open(env_file, "a") as env_file:
            env_file.write(f"new_release=true\npackage_name={package_name}\npackage_version={package_version}\n")
    else:
        print(f"No release needed for {package_name} {package_version}")
        with open(env_file, "a") as env_file:
            env_file.write("new_release=false")