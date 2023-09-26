import sqlite3

from pathlib import Path
from hermes.core import fields, tables
from hermes.core.scrapers import BaseScraper

import logging

class BaseStorage():
    fields = None
    row_factory = sqlite3.Row
    DB_NAME = "sqlite3.db"

    def __init__(self, parent_dir: str) -> None:
        self.database_path = Path(parent_dir, self.DB_NAME)
        self.base_fields = None
        self.custom_fields = None


        self.tables = {
            "scrapers":
                tables.BaseTable(name="Scrapers", fields=
                [
                    fields.IntegerFieldSQLite(name="scraper_id", primary_key=True),
                    fields.TextFieldSQLite(name="scraper_url", null=False),
                    fields.TextFieldSQLite(name="scraper_name", null=False, use_to_identify=True),
                    fields.TextFieldSQLite(name="scraper_verbose_name", null=False),
                ]),
            "articles":
                tables.BaseTable(name="Articles", fields=[
                    fields.IntegerFieldSQLite(name="id", primary_key=True),
                    fields.BoolFieldSQLite(name="is_new", null=False),
                    fields.IntegerFieldSQLite(name="scraper", null=False, use_to_identify=True),
                    fields.ConstraintField(constraint="FOREIGN KEY (scraper) REFERENCES Scrapers (id) ON DELETE CASCADE"),
                ]),
        }

        self.update_custom_fields()

        self.conn = None


    def connect(self) -> sqlite3.Connection:
        try:
            self.conn = sqlite3.connect(str(self.database_path))
            self.conn.row_factory = self.row_factory
            self.conn.set_trace_callback(logging.debug)
        except sqlite3.Error as e:
            raise e

        return self.conn

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args, **kwargs):
        self.conn.close()
    
    def delete_table(self, table:tables.BaseTable, perform: bool=False):
        c = self.conn.cursor()
        
        if perform:
            c.execute(f"DROP TABLE IF EXISTS {table.name}")

    def delete_db(self, perform: bool=False):
        for key, table in self.tables.items():
            self.delete_table(table, perform)
    
    def get_all_rows(self) -> list:
        rv = []

        for key, table in self.tables.items():
            rv.append(self.get_all_rows_in_table(table))

        return rv

    def get_all_rows_in_table(self, table: tables.BaseTable) -> list:
        c = self.conn.cursor()
 
        c.execute(f"SELECT * FROM {table.name}")

        return c.fetchall()

    def get_new(self) -> tuple:
        c = self.conn.cursor()
        c.execute(f"SELECT * FROM {self.tables['articles'].name} a JOIN {self.tables['scrapers'].name} s on a.scraper = s.scraper_id WHERE is_new=1")
        
        rv = c.fetchall()
        return rv  

    def insert_row(self, row: dict, table_name: str) -> None:
        c = self.conn.cursor()

        # dynamically construct a query based on row size which later can be parametrized
        field = ', '.join([k for k in row.keys()])
        questions_marks = ', '.join(['?' for i in row.values()])
        sql = f"INSERT INTO {table_name}({field}) VALUES ({questions_marks});"

        c.execute(sql, (*row.values(),))

        self.conn.commit()

    def mark_old(self, row: tuple, allow_multiple_rows=False) -> None:
        c = self.conn.cursor()
        id = row['id'] 
        c.execute(f"UPDATE {self.tables['articles'].name} SET is_new=? WHERE id=?", (False, id))
        if c.rowcount == 1 or allow_multiple_rows:
            self.conn.commit()

    def mark_old_all(self) -> None:
        for row in self.get_new():
            self.mark_old(row)


    def create_tables_if_not_exist(self) -> None:
        c = self.conn.cursor()

        for key, table in self.tables.items():

            # create a string of all field that can be directly appended to sql query
            field_strings = []
            for field in table.get_fields():
                field_str = field.get_field_as_string()
                field_strings.append(field_str)

            fields = ', '.join(field_strings)
            sql = f"CREATE TABLE IF NOT EXISTS {table.name} ({fields});"

            c.execute(sql)
        
        self.conn.commit()

    def update_or_create_scrapers(self, scrapers: list) -> None:
        c = self.conn.cursor()

        for scraper in scrapers:
            scraper_attrs = scraper.get_attrs_as_dict()

            row = [(field.name, scraper_attrs.get(field.name)) for field in self.tables['scrapers'].get_fields()]
            row = dict(row)

            # Check is there is a scraper with identical name but different parameters, replace it if there is
            sql = f"SELECT * FROM {self.tables['scrapers'].name} WHERE "

            sql += " AND ".join([str(field.name)+"=?" for field in self.tables['scrapers'].get_identification_fields()])

            values = [scraper.get_attrs_as_dict().get(field.name) for field in self.tables['scrapers'].get_identification_fields()]

            c.execute(sql, values)
            similar_scraper = c.fetchone()
        
            pk = self.tables['scrapers'].get_primary_key_field()
            if similar_scraper != None:
                new_id = similar_scraper[pk.name]

                # just delete the similar row and replace it with a new one, its easier to program than UPDATE queries
                # there should be little scrapers to replace, so it doesnt have to be perfectly efficient
                c.execute(f"DELETE FROM {self.tables['scrapers'].name} WHERE {pk.name}=?", (new_id,))
                if c.rowcount == 1:
                    row.update(
                        {pk.name: new_id}
                    ) 
                    self.conn.commit()
                else:
                    raise Exception("Too many rows affected")

            self.insert_row(row, self.tables['scrapers'].name)

    def update_custom_fields(self) -> list:
        if self.fields == None:
            raise NotImplementedError("`fields` property must be defined in the storage class")

        self.custom_fields = self.fields

        for field in self.custom_fields:
            self.tables['articles'].add_field(field)

        return self.custom_fields

    def store(self, data: dict, scraper: BaseScraper) -> None:
        c = self.conn.cursor()

        for row in data:
            pk = self.tables['scrapers'].get_primary_key_field()
            sql = f"SELECT {pk.name} FROM {self.tables['scrapers'].name} WHERE "

            sql += " AND ".join([str(field.name)+"=?" for field in self.tables['scrapers'].get_identification_fields()])

            values = [scraper.get_attrs_as_dict().get(field.name) for field in self.tables['scrapers'].get_identification_fields()]

            c.execute(sql, values)
            scraper_id = int(c.fetchone()[0])
            row['scraper'] = scraper_id


            sql = f"SELECT 1 FROM {self.tables['articles'].name} WHERE "

            sql += " AND ".join([str(field.name)+"=?" for field in self.tables['articles'].get_identification_fields()])

            values = [row.get(field.name) for field in self.tables['articles'].get_identification_fields()]
            c.execute(sql, values)
            
            articles = c.fetchall()

            if len(articles) == 0:
                row['is_new'] = True
                self.insert_row(row, self.tables['articles'].name)


class SimpleStorage(BaseStorage):
    pass