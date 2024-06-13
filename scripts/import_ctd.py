import json
import os
import struct
from typing import Any
from helper import DIR_EXPORT_ROOT, DIR_IMPORT_ROOT


def import_ctd(input_root: str, message_root: str, output_root: str):
  for root, dirs, files in os.walk(input_root):
    for file_name in files:
      if not file_name.endswith(".ctd"):
        continue

      sheet_name = os.path.relpath(f"{root}/{file_name}", input_root).replace("\\", "/")
      json_path = f"{message_root}/{sheet_name}.json"
      if not os.path.exists(json_path):
        continue

      with open(json_path, "r", -1, "utf8") as reader:
        texts: list[dict[str, Any]] = json.load(reader)["texts"]

      with open(f"{root}/{file_name}", "rb") as reader:
        binary = bytearray(reader.read())

      size, rows = struct.unpack_from("<2I", binary)
      row_size = size // rows
      if row_size != 0x40 or size % rows != 0 or size + 0x20 > len(binary):
        continue
      size_2, rows_2 = struct.unpack_from("<2I", binary, size + 0x10)
      if size != size_2 or rows != rows_2:
        continue

      for i in range(rows):
        binary[0x10 + i * row_size:0x10 + (i + 1) * row_size] = texts[i]["lines"][0].encode("cp932").rjust(row_size, b"\0")
      
      new_path = f"{output_root}/{sheet_name}"
      os.makedirs(os.path.dirname(new_path), exist_ok=True)
      with open(new_path, "wb") as writer:
        writer.write(binary)


if __name__ == "__main__":
  import_ctd(DIR_EXPORT_ROOT, DIR_IMPORT_ROOT, DIR_IMPORT_ROOT)
