import os
import sys

from configs import *
from blocks.base.version import VersionManager


if __name__ == "__main__":
        
    print('\nTEST Version')
    version = VersionManager(current_version="0.0.1")
    print("Current Version:", version.current_version)
    print("Is Up-to-date:", version.get_version())
    print("Changelog:", version.get_changelog())
    
    print('\nTEST Version')
    version.upgrade_version("0.0.2", "Added new features and fixed bugs.")
    print("Upgraded Version:", version.current_version)
    print("Is Up-to-date after upgrade:", version.get_version())

    print('\nTEST Version')
    print("Changelog:", version.get_changelog())

    print('\nTEST Version')
    version.upgrade_version("0.1.0", "Major update with breaking changes.")
    print("Upgraded Version:", version.current_version)
    print("Is Up-to-date after second upgrade:", version.get_version())
    print("Changelog:", version.get_changelog())

    print('\nTEST Version')
    version.save_to_file("version_info.json")
    loaded_version = VersionManager.load_from_file("version_info.json")
    print("Loaded Version from file:", loaded_version.current_version)
    print("Loaded Changelog:", loaded_version.get_changelog())

    print('\nTEST Version')
    version.export_to_markdown("version_changelog.md")
    print("Changelog exported to version_changelog.md")

    print('\nTEST Version')
    print(version.increment_version(minor=True,))


