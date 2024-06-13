import json
import os
import struct
from helper import DIR_EXPORT_ROOT


def export_ctd(input_root: str, message_root: str):
  for root, dirs, files in os.walk(input_root):
    for file_name in files:
      if not file_name.endswith(".ctd"):
        continue

      sheet_name = os.path.relpath(f"{root}/{file_name}", input_root).replace("\\", "/")
      with open(f"{root}/{file_name}", "rb") as reader:
        binary = reader.read()

      size, rows = struct.unpack_from("<2I", binary)
      row_size = size // rows
      if row_size != 0x40 or size % rows != 0 or size + 0x20 > len(binary):
        continue
      size_2, rows_2 = struct.unpack_from("<2I", binary, size + 0x10)
      if size != size_2 or rows != rows_2:
        continue

      texts = []
      for i in range(rows):
        text_bytes = binary[0x10 + i * row_size:0x10 + (i + 1) * row_size].rstrip(b"\0")
        texts.append({
          "id": f"text_{i:03d}",
          "speaker": "",
          "lines": [text_bytes.decode("cp932")],
          "index": i,
        })

      new_path = f"{message_root}/{sheet_name}.json"
      os.makedirs(os.path.dirname(new_path), exist_ok=True)
      with open(new_path, "w", -1, "utf8") as writer:
        json.dump({
          "speakers": [],
          "texts": texts,
        }, writer, ensure_ascii=False, indent=2)


if __name__ == "__main__":
  export_ctd(DIR_EXPORT_ROOT, DIR_EXPORT_ROOT)
