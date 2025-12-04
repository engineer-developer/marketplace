FROM postgres:17

# Для инициализации базы данных из дампа с помощь sql-скрипта
#COPY init.sql /docker-entrypoint-initdb.d/init.sql

COPY postgresql.conf pg_hba.conf /var/etc/postgres/

CMD ["postgres", "-c", "config_file=/var/etc/postgres/postgresql.conf", \
                 "-c", "hba_file=/var/etc/postgres/pg_hba.conf"]
