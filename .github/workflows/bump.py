#!/usr/bin/python

import subprocess
import re
import sys
import os

def convert_version_to_sortable_int(major, minor):
    return major * 1000 + minor

def determine_most_recent_existing_version():
    tags = subprocess.run(["git", "tag"], capture_output=True).stdout.splitlines()

    versions = []

    for t in tags:
        tag = t.decode()
        if re.match(r"v[0-9]+.[0-9]+", tag):
            tag_without_prefix = tag[1:]
            components = tag_without_prefix.split(".")
            assert len(components) == 2
            print(components)
            major_int = int(components[0])
            minor_int = int(components[1])
            versions.append(
                {
                    "tag": tag,
                    "sortNumber": convert_version_to_sortable_int(major_int, minor_int),
                    "major": major_int,
                    "minor": minor_int,
                }
            )

    def key(v):
        return v["sortNumber"]

    versions.sort(key=key, reverse=True)
    print(versions)
    return versions[0]


def bump(most_recent_version, component_to_bump):
    new_version = ""

    if component_to_bump == "major":
        new_major = most_recent_version["major"] + 1
        new_version = f"v{new_major}.0"
    elif component_to_bump == "minor":
        new_minor = most_recent_version["minor"] + 1
        major = most_recent_version["major"]
        new_version = f"v{major}.{new_minor}"
    else:
        raise (f'Invalid component provided: {component_to_bump}, only major or minor are supported.')

    return new_version


def determine_component_to_bump():
    if sys.argv[1] not in ["major", "minor"]:
        raise ("Usage: bump.py (major|minor)")
    return sys.argv[1]


def main():
    component_to_bump = determine_component_to_bump()
    most_recent_version = determine_most_recent_existing_version()
    new_version = bump(most_recent_version, component_to_bump)

    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as file_handle:
            print(f"newVersion={new_version}", file=file_handle)
    else:
        print(f"No GitHub env found. New version is {new_version}")


if __name__ == "__main__":
    main()
