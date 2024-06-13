import json
from logging import warning
import os
from typing import Any
from helper import CODE_BIN_PATH, CONTROL_PATTERN, DIR_MESSAGE_NEW_ROOT, DIR_PATCH_ROOT


def import_code_bin(code_bin_path: str, message_root: str, output_root: str):
  with open(code_bin_path, "rb") as reader:
    binary = bytearray(reader.read())

  with open(f"{message_root}/code.bin.json", "r", -1, "utf8") as reader:
    texts: list[dict[str, Any]] = json.load(reader)["texts"]

  for item in texts:
    offset: int = item["offset"]
    length: int = item["length"]
    text: str = item["lines"][0].replace("{", "[").replace("}", "]")
    text_bytes = bytearray()
    splited = CONTROL_PATTERN.split(text)
    for i, part in enumerate(splited):
      if i % 2 == 0:
        text_bytes += part.encode("cp932")
      elif part == "\n":
        text_bytes += b"\n"
      else:
        assert part.startswith("[") and part.endswith("]")
        text_bytes += bytes.fromhex(part[1:-1])
    if len(text_bytes) > length:
      warning(f"Text is too long: {text}")
      continue
    elif len(text_bytes) < length:
      text_bytes += b"\0" * (length - len(text_bytes))

    binary[offset:offset + length] = text_bytes

  os.makedirs(f"{output_root}/exefs", exist_ok=True)
  with open(f"{output_root}/exefs/code.bin", "wb") as writer:
    writer.write(binary)


if __name__ == "__main__":
  import_code_bin(CODE_BIN_PATH, DIR_MESSAGE_NEW_ROOT, DIR_PATCH_ROOT)
