import json
import re

DIR_ORIGINAL_ROOT = "original_files/unpacked"
DIR_MESSAGE_ROOT = "temp/messages"
DIR_MESSAGE_NEW_ROOT = "temp/messages_new"
DIR_JSON_ROOT = "files/normalized"
DIR_CSV_ROOT = "texts"

ZH_HANS_2_KANJI_PATH = "files/zh_Hans_2_kanji.json"
CHAR_TABLE_PATH = "out/char_table.json"

CONTROL_PATTERN = re.compile(r"(\[[0-9A-F]{2}(?: [0-9A-F]{2})*\]|\n)")
TRASH_PATTERN = re.compile(
  r"^(?:|.*(?:0x|＿|※|（仮）|ダミーメッセージ|ダミーMSG|ダミー枠|ＲＥＳＥＲＶＥ|リザーブ|ダ\[(?:n|e|f(?: \d+)+)\]ミ\[(?:n|e|f(?: \d+)+)\]ー|★未使用|MSG).*|ダミー\d*|＜声のみ＞ダミー|会話ダミー|ダミ－|ブランク|未使用)$",
  re.DOTALL,
)
KANA_PATTERN = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]+")
CHINESE_TO_JAPANESE = {
  "·": "・",
  "—": "―",
}

char_table_reversed: dict[str, str] = {}
zh_hans_no_code = set()


def remove_controls(line: str) -> tuple[str, str, str]:
  splited: list[str] = CONTROL_PATTERN.split(line)

  start = 0
  while start < len(splited):
    part = splited[start].strip()
    if part.startswith("[F2 44 ") or (part and not part.startswith("[")):
      break
    start += 1
  end = len(splited) - 1
  while end >= start:
    part = splited[end].strip()
    if part.startswith("[F2 44 ") or (part and not part.startswith("[")):
      break
    end -= 1

  return (
    "".join(splited[:start]),
    "".join(splited[start:end + 1]),
    "".join(splited[end + 1:]),
  )


def convert_zh_hans_to_shift_jis(zh_hans: str) -> str:
  global char_table_reversed
  if len(char_table_reversed) == 0:
    with open(CHAR_TABLE_PATH, "r", -1, "utf8") as reader:
      char_table: dict[str, str] = json.load(reader)
      for k, v in char_table.items():
        char_table_reversed[v] = k

  output = []
  for char in zh_hans:
    char = CHINESE_TO_JAPANESE.get(char, char)
    if char in char_table_reversed:
      output.append(char_table_reversed[char])
    else:
      try:
        char.encode("cp932")
        output.append(char)
      except UnicodeEncodeError:
        if char not in zh_hans_no_code:
          print(f"Missing char: {char}")
          zh_hans_no_code.add(char)
        output.append("?")

  return "".join(output)
