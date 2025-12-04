import json
from pathlib import Path


DEPRECATED_MODELS_NAMES = [
    "admin.logentry",
    "auth.permission",
    "contenttypes.contenttype",
    "sessions.session",
]

INPUT_FILENAME = "db_data_full.json"
OUTPUT_FILENAME = "output_file_fixture.json"
BASE_DIR = Path(__file__).parent


class Filter:
    """Класс для фильтрации содержимого JSON файла"""

    def __init__(self, input_file, output_file, deprecated_names: list[str]):
        self.input_file = input_file
        self.output_file = output_file
        self.deprecated_names = deprecated_names

    @staticmethod
    def read_from_file(file: Path) -> list[dict]:
        """Получаем содержимое файла"""

        with file.open("r", encoding="utf-8") as f:
            items = json.load(f)
        return items

    @staticmethod
    def filter_values(items: list[dict], deprecated_names: list[str]) -> list[dict]:
        """Выполняем фильтрацию"""

        new_items: list = []
        for item in items:
            if item["model"] not in deprecated_names:
                new_items.append(item)
        return new_items

    @staticmethod
    def write_to_file(file, value) -> bool:
        """Записываем результат в новый файл"""

        with file.open("w", encoding="utf-8") as f:
            json.dump(value, f, indent=4, ensure_ascii=False)
        return True

    def processing_file(self):
        """
        Функция удаляет из списка те словари, значение поля 'model' которых
        соответствует одному из значений в 'DEPRECATED_MODELS_NAMES'
        """
        items = self.read_from_file(self.input_file)
        new_items = self.filter_values(items, self.deprecated_names)
        result = self.write_to_file(self.output_file, new_items)
        if result:
            print("Выполнено успешно")


if __name__ == "__main__":
    input_file_path = BASE_DIR / INPUT_FILENAME
    output_file_path = BASE_DIR / OUTPUT_FILENAME

    Filter(
        input_file=input_file_path,
        output_file=output_file_path,
        deprecated_names=DEPRECATED_MODELS_NAMES,
    ).processing_file()
