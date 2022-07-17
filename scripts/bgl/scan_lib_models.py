"""
Analyze the fsx addon scenery folder for various kinds of errors in scenery object libraries and placement files
"""
import logging
import os

from bgl.helpers.model_db import ModelsDB

from fs_parse.utils import FSX_ADDON_SCENERY_DIR, FSX_STOCK_SCENERY_DIR, configure_logging

# TODO: transform these into CLI arguments
SHOW_DUPLICATE_DEFINITIONS = True
SHOW_NONLOCAL_PLACEMENTS = True
FIND_DUPLICATE_LIBS = True
FIND_DIFFERENT_LIBS_WITH_SAME_NAME = True


def shorten_file(filepath: str) -> str:
    return filepath.replace(FSX_ADDON_SCENERY_DIR, "")


def find_duplicate_libs(db: ModelsDB):
    """
     Find bgl files which declare the same set of scenery objects.
     Note that this function does not check for duplicate files, only the uuids are considered for object comparison.
     Other sections of the bgl files may still be different.
    """
    duplicate_libraries = []
    files = sorted(db.file_2_uuids.keys())
    visited = []
    for file in files:
        if file in visited:
            continue
        duplicates_set = []
        for file_2 in [f for f in files if f != file and f not in visited]:
            if sorted(db.file_2_uuids[file]) == sorted(db.file_2_uuids[file_2]):
                if not duplicates_set:
                    duplicates_set.append(file)
                duplicates_set.append(file_2)
                visited.append(file_2)
        if duplicates_set:
            duplicate_libraries.append(duplicates_set)
        visited.append(file)
    print("These libraries contain the exact same set of UUIDs (NOTE: actual object data may still be different):")
    for duplicates_set in duplicate_libraries:
        print()
        for p in duplicates_set:
            print(shorten_file(p))


def show_nonlocal_placements(db: ModelsDB):
    """
     Print placement files which reference (non-stock) objects not found in the same folder, or not found at all.
    """
    for placement_file_path, placed_uuids in db.file_2_placements.items():
        if not placement_file_path.startswith(FSX_STOCK_SCENERY_DIR):
            placement_dir, placement_filename = os.path.split(placement_file_path)
            for placed_uuid in placed_uuids:
                try:
                    definition_files = db.uuid_2_files[placed_uuid]
                except KeyError:
                    print(f"Object {placed_uuid} definition not found (referenced by placement file {shorten_file(placement_file_path)})")
                    continue

                if any([
                    definition_file.lower().startswith(FSX_STOCK_SCENERY_DIR.lower())
                    for definition_file in definition_files
                ]):
                    continue  # stock object, go to the next one

                if not any([
                    os.path.split(definition_file)[0] == placement_dir
                    for definition_file in definition_files
                ]):
                    print(f"Placement {shorten_file(placement_file_path)} references an object from outside its folder: {placed_uuid} defined in:")
                    for f in db.uuid_2_files[placed_uuid]:
                        print(f"\t{f}")


def find_different_libs_with_same_name(db: ModelsDB):
    """
     Find .bgl files with same name but different sets of library objects UUIDs
     Only the differences are printed.
     If an UUID is in the output, it means that it is missing from at least one of the other files with the same name.
     This means that if a file shows no UUIDs, all its objects are defined in every other file with the same name.
    """
    filenames_2_uuid_sets = {}
    for path, uuids in db.file_2_uuids.items():
        folder, filename = os.path.split(path)
        filenames_2_uuid_sets[filename] = filenames_2_uuid_sets.get(filename, []) + [" ".join(sorted(uuids))]
    print("These files have the same names but different contents (potentially different versions of the same libraries):")
    for filename, files in filenames_2_uuid_sets.items():
        if len(set(files)) > 1:
            print(f"These uuids are missing from the different versions of {filename}:")
            same_name_entries = [f for f in db.files if os.path.split(f)[1] == filename]
            for filepath in same_name_entries:
                all_except_it = [db.file_2_uuids[f] for f in same_name_entries if f != filepath]
                nonshared_guids = []
                for guid in db.file_2_uuids[filepath]:
                    is_missing_from_one_of_the_others = not all([guid in s for s in all_except_it])
                    if is_missing_from_one_of_the_others:
                        nonshared_guids.append(guid)
                print(f"\t{shorten_file(filepath)}")
                print("\t" + " ".join(nonshared_guids))


def show_duplicate_definitions(db: ModelsDB):
    """ Print UUID objects defined in more than one library file """
    duplicate_definitions = {
        uuid: files
        for uuid, files in db.uuid_2_files.items()
        if len(files) > 1
    }
    for placed_uuid, files in duplicate_definitions:
        print(f"Object {placed_uuid} is defined in more than one file:")
        for file in files:
            print(f"\t{shorten_file(file)}")
        print()


def main():
    configure_logging(level=logging.INFO)

    db = ModelsDB(include_stock=True,
                  include_addon=True)

    if SHOW_DUPLICATE_DEFINITIONS:
        show_duplicate_definitions(db)

    if SHOW_NONLOCAL_PLACEMENTS:
        show_nonlocal_placements(db)

    if FIND_DUPLICATE_LIBS:
        find_duplicate_libs(db)

    if FIND_DIFFERENT_LIBS_WITH_SAME_NAME:
        find_different_libs_with_same_name(db)


if __name__ == '__main__':
    main()
