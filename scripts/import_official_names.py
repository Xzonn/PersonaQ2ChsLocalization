import csv
import os

from helper import DIR_CSV_ROOT, DIR_OFFICIAL_TRANSLATIONS_ROOT, load_csv

LANGUAGE = os.getenv("XZ_LANGUAGE") or "zh_Hans"


def load_official_names(root: str) -> dict[str, dict[str, str]]:
  translations: dict[str, dict[str, str]] = {}
  for file_name in sorted(os.listdir(root)):
    if not file_name.endswith(".csv"):
      continue

    source = file_name.split(".", 1)[0].split("_", 1)[-1]
    with open(f"{root}/{file_name}", "r", -1, "utf-8-sig", "ignore", "") as csvfile:
      reader = csv.reader(csvfile)

      row_iter = reader
      headers = next(row_iter)
      for row in row_iter:
        item_dict = dict(zip(headers, row))
        ja, zh = item_dict["ja"], item_dict["zh_Hans"]
        if ja in translations:
          continue
        translations[ja] = {
          "translation": zh,
          "source": source,
        }

  return translations


def import_official_names(csv_root_without_language: str, language: str, official_translations_root: str):
  translations = load_official_names(official_translations_root)
  for root, dirs, files in os.walk(f"{csv_root_without_language}/{language}"):
    for file_name in files:
      if not file_name.endswith(".csv"):
        continue

      sheet_name = os.path.relpath(
        f"{root}/{file_name}",
        f"{csv_root_without_language}/{language}",
      ).replace("\\", "/").removesuffix(".csv")

      original = load_csv(f"{csv_root_without_language}/ja", sheet_name)
      translated = load_csv(f"{csv_root_without_language}/{language}", sheet_name)

      csvfile = open(f"{root}/{file_name}", "w", -1, "utf-8", None, "")
      writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, lineterminator="\n")
      writer.writerow(("source", "target", "id", "developer_comments"))
      for i, (original_line, translated_line) in enumerate(zip(original, translated)):
        line_id = original_line["id"]
        ja = original_line["target"]
        zh = translated_line["target"]
        comments = translated_line["developer_comments"]

        if ja in translations:
          zh = translations[ja]["translation"]
          comments = f"翻译匹配：{translations[ja]['source']}"

        writer.writerow((line_id, zh, line_id, comments))

      csvfile.close()


if __name__ == "__main__":
  import_official_names(DIR_CSV_ROOT, LANGUAGE, DIR_OFFICIAL_TRANSLATIONS_ROOT)
