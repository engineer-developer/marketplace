# Примеры экспорта и импорта данных 
## 1. Экспорт данных из базы данных в фикстуру
### 1.1. Создание фикстуры со всеми значениями базы данных
```
python manage.py dumpdata --natural-foreign --natural-primary --indent 4 --output fixtures/db_data_full.json
```

### 1.2. Создание фикстуры со значениями базы данных с исключением отдельных элементов
> Исключенные элементы:
> - auth.permission
> - contenttypes
```
python manage.py dumpdata --indent 4 --exclude=auth.permission --exclude=contenttypes --output fixtures/db_data_without_auth-perm_content-types.json
```

### 1.3. Создание фикстуры со значениями базы данных с исключением отдельных элементов
> Исключенные элементы:
> - auth.permission
> - contenttypes
> - admin
```
python manage.py dumpdata --indent 4 --exclude=auth.permission --exclude=contenttypes --exclude=admin --output fixtures/db_data_without_auth-perm_content-types_admin.json
```

## 2. Импорт данных в базу данных из фикстуры 
### 2.1. Загрузка данных из фикстуры со всеми значениями базы данных
```
python manage.py loaddata fixtures/db_data_full.json
```
### 2.2. Загрузка данных из фикстуры db_data_without_auth-perm_content-types.json
```
python manage.py loaddata fixtures/db_data_without_auth-perm_content-types.json
```
### 2.3. Загрузка данных из фикстуры db_data_without_auth-perm_content-types_admin.json
```
python manage.py loaddata fixtures/db_data_without_auth-perm_content-types_admin.json
```