import csv
import json
import re

DIR_ORIGINAL_ROOT = "original_files/unpacked"
DIR_MESSAGE_ROOT = "temp/messages"
DIR_MESSAGE_NEW_ROOT = "temp/messages_new"
DIR_JSON_ROOT = "files/normalized"
DIR_CSV_ROOT = "texts"
DIR_XLSX_ROOT = "out/xlsx"

ZH_HANS_2_KANJI_PATH = "files/zh_Hans_2_kanji.json"
DUPLICATE_FILES_INFO_PATH = "files/duplicate_files.json"
CHAR_TABLE_PATH = "out/char_table.json"

CONTROL_PATTERN = re.compile(r"(\[[0-9A-F]{2}(?: [0-9A-F]{2})*\]|\n)")
TRASH_PATTERN = re.compile(
  r"^(?:|.*(?:0x|＿|※|（仮）|ダミーメッセージ|ダミーMSG|ダミー枠|ＲＥＳＥＲＶＥ|リザーブ|ダ\[(?:n|e|f(?: \d+)+)\]ミ\[(?:n|e|f(?: \d+)+)\]ー|★未使用|MSG).*|ダミー\d*|＜声のみ＞ダミー|会話ダミー|ダミ－|ブランク|未使用)$",
  re.DOTALL,
)
KANA_PATTERN = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]+")
SPECLAL_CONTROL_PATTERN = re.compile(r"^\[(?:P[345]P?[姓名全]|(?:占位[A-B]|颜色) [0-9A-F]{2})\]$")
CHINESE_TO_JAPANESE = {
  "·": "・",
  "—": "―",
}

TO_SPECIAL_CONTROLS = {
  r"\[F5 C1 0D 01 01 01 01 01 01 01\]": "[P4姓]",
  r"\[F5 C1 0E 01 01 01 01 01 01 01\]": "[P4名]",
  r"\[F5 C1 0F 01 01 01 01 01 01 01\]": "[P4全]",
  r"\[F5 C1 10 01 01 01 01 01 01 01\]": "[P3姓]",
  r"\[F5 C1 11 01 01 01 01 01 01 01\]": "[P3名]",
  r"\[F5 C1 12 01 01 01 01 01 01 01\]": "[P3全]",
  r"\[F5 C1 1B 01 01 01 01 01 01 01\]": "[P3P姓]",
  r"\[F5 C1 1C 01 01 01 01 01 01 01\]": "[P3P名]",
  r"\[F5 C1 1D 01 01 01 01 01 01 01\]": "[P3P全]",
  r"\[F5 C1 1E 01 01 01 01 01 01 01\]": "[P5姓]",
  r"\[F5 C1 1F 01 01 01 01 01 01 01\]": "[P5名]",
  r"\[F5 C1 20 01 01 01 01 01 01 01\]": "[P5全]",
  r"\[F2 44 ([0-9A-F]{2}) 01\]": r"[占位A \1]",
  r"\[F4 45 04 01 00 00 ([0-9A-F]{2}) 01\]": r"[占位B \1]",
  r"\[F2 01 ([0-9A-F]{2}) 01\]": r"[颜色 \1]",
}
TO_NORMAL_CONTROLS = {
  r"\[P4姓\]": "[F5 C1 0D 01 01 01 01 01 01 01]",
  r"\[P4名\]": "[F5 C1 0E 01 01 01 01 01 01 01]",
  r"\[P4全\]": "[F5 C1 0F 01 01 01 01 01 01 01]",
  r"\[P3姓\]": "[F5 C1 10 01 01 01 01 01 01 01]",
  r"\[P3名\]": "[F5 C1 11 01 01 01 01 01 01 01]",
  r"\[P3全\]": "[F5 C1 12 01 01 01 01 01 01 01]",
  r"\[P3P姓\]": "[F5 C1 1B 01 01 01 01 01 01 01]",
  r"\[P3P名\]": "[F5 C1 1C 01 01 01 01 01 01 01]",
  r"\[P3P全\]": "[F5 C1 1D 01 01 01 01 01 01 01]",
  r"\[P5姓\]": "[F5 C1 1E 01 01 01 01 01 01 01]",
  r"\[P5名\]": "[F5 C1 1F 01 01 01 01 01 01 01]",
  r"\[P5全\]": "[F5 C1 20 01 01 01 01 01 01 01]",
  r"\[占位A ([0-9A-F]{2})\]": r"[F2 44 \1 01]",
  r"\[占位B ([0-9A-F]{2})\]": r"[F4 45 04 01 00 00 \1 01]",
  r"\[颜色 ([0-9A-F]{2})\]": r"[F2 01 \1 01]",
}

char_table_reversed: dict[str, str] = {}
zh_hans_no_code = set()


def convert_special_controls(line: str) -> str:
  line = line.replace("{", "[").replace("}", "]")
  for k, v in TO_SPECIAL_CONTROLS.items():
    line = re.sub(k, v, line)
  return line


def convert_back_special_controls(line: str) -> str:
  for k, v in TO_NORMAL_CONTROLS.items():
    line = re.sub(k, v, line)
  line = line.replace("[", "{").replace("]", "}")
  return line


def remove_controls(line: str) -> tuple[str, str, str]:
  splited: list[str] = CONTROL_PATTERN.split(line)

  start = 0
  while start < len(splited):
    part = splited[start].strip()
    if part and start % 2 == 0 and not SPECLAL_CONTROL_PATTERN.search(part):
      break
    start += 1
  end = len(splited) - 1
  while end >= start:
    part = splited[end].strip()
    if part and end % 2 == 0 and not SPECLAL_CONTROL_PATTERN.search(part):
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
  control = False
  for char in zh_hans:
    if char == "[":
      control = True
    if control:
      output.append(char)
      if char == "]":
        control = False
      continue

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


def load_translations(root: str, sheet_name: str) -> dict[str, str]:
  with open(f"{root}/{sheet_name}.csv", "r", -1, "utf8", "ignore", "") as csvfile:
    reader = csv.reader(csvfile)

    row_iter = reader
    headers = next(row_iter)
    translations = {}
    for row in row_iter:
      item_dict = dict(zip(headers, row))
      translations[item_dict["id"]] = item_dict["target"].replace("\\r", "\r")

  return translations


def load_csv(root: str, sheet_name: str) -> list[dict[str, str]]:
  with open(f"{root}/{sheet_name}.csv", "r", -1, "utf8", "ignore", "") as csvfile:
    reader = csv.reader(csvfile)

    row_iter = reader
    headers = next(row_iter)
    lines = []
    for row in row_iter:
      item_dict = dict(zip(headers, row))
      lines.append(item_dict)

  return lines
