import json
from csv import DictReader
from io import TextIOWrapper

from catalog_app.models import Category


def is_category_exists(title: str) -> bool:
    """Проверка существования категории в базе данных"""

    category = Category.objects.filter(title=title).first()
    return category is not None


def save_csv_categories(file, encoding) -> list[Category | None]:
    """
    Функция извлекает данные из CSV файла и создает категории,
    если они не существуют в базе данных
    """

    csv_file = TextIOWrapper(
        buffer=file,
        encoding=encoding,
    )
    reader = DictReader(csv_file, delimiter=";")

    created_categories = []
    for row in reader:
        title_value = row["title"]
        if not is_category_exists(title_value):
            parent_value = row["parent"]
            parent, created = Category.objects.get_or_create(title=parent_value)
            if created:
                created_categories.append(parent)
            category = Category(
                title=title_value,
                parent=parent,
            )
            category.save()
            created_categories.append(category)

    return created_categories


def save_json_categories(file, encoding) -> list[Category | None]:
    """
    Функция извлекает данные из JSON файла и создает категории,
    если они не существуют в базе данных
    """

    json_file = TextIOWrapper(buffer=file, encoding=encoding)
    categories_data: dict[str, list[str]] = json.load(json_file)

    created_categories = []
    for category, sub_categories in categories_data.items():
        parent, parent_created = Category.objects.get_or_create(title=category)
        if parent_created:
            created_categories.append(parent)

        for sub_category in sub_categories:
            child, child_created = Category.objects.get_or_create(title=sub_category)
            if child_created:
                child.parent = parent
                child.save()
                created_categories.append(child)

    return created_categories
