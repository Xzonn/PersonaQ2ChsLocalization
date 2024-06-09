import csv
import json
import os

from helper import DIR_CSV_ROOT, DIR_JSON_ROOT

LANGUAGE = os.getenv("XZ_LANGUAGE") or "zh_Hans"


def load_translations(root: str, sheet_name: str) -> bool:
  with open(f"{root}/{sheet_name}.csv", "r", -1, "utf8", "ignore", "") as csvfile:
    reader = csv.reader(csvfile)

    row_iter = reader
    headers = next(row_iter)
    translations: dict[str, str] = {}
    for row in row_iter:
      item_dict = dict(zip(headers, row))
      translations[item_dict["id"]] = item_dict["target"].replace("\\r", "\r")

  return translations


def import_csv_to_json(csv_root: str, json_input_root: str, json_output_root: str):
  for root, dirs, files in os.walk(csv_root):
    for file_name in files:
      if not file_name.endswith(".csv"):
        continue

      sheet_name = os.path.relpath(f"{root}/{file_name}", csv_root).replace("\\", "/").removesuffix(".csv")
      print(f"Importing: {sheet_name}.csv")

      translations = load_translations(csv_root, sheet_name)

      with open(f"{json_input_root}/{sheet_name}.json", "r", -1, "utf8") as reader:
        json_input = json.load(reader)

      for k, v in json_input.items():
        if v.get("trash", False):
          continue
        if k in translations:
          v["content"] = translations[k]

      output_path = f"{json_output_root}/{sheet_name}.json"
      os.makedirs(os.path.dirname(output_path), exist_ok=True)
      with open(output_path, "w", -1, "utf8") as writer:
        json.dump(json_input, writer, ensure_ascii=False, indent=2)


if __name__ == "__main__":
  import_csv_to_json(f"{DIR_CSV_ROOT}/{LANGUAGE}", f"{DIR_JSON_ROOT}/ja", f"{DIR_JSON_ROOT}/{LANGUAGE}")
