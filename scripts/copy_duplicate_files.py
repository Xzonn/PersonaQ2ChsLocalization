import json
import os
import shutil

from helper import DIR_MESSAGE_NEW_ROOT, DUPLICATE_FILES_INFO_PATH


def copy_duplicate_files(root: str, info_path: str):
  with open(info_path, "r", -1, "utf8") as reader:
    duplicate_files: list[list[str]] = json.load(reader)

  for sub_list in duplicate_files:
    source_path = f"{root}/{sub_list[0]}.json"
    for file_path in sub_list[1:]:
      full_path = f"{root}/{file_path}.json"
      os.makedirs(os.path.dirname(full_path), exist_ok=True)
      shutil.copyfile(source_path, full_path)


if __name__ == "__main__":
  copy_duplicate_files(DIR_MESSAGE_NEW_ROOT, DUPLICATE_FILES_INFO_PATH)
