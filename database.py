import os
import sqlite3
from data_clean import data_clean
from classes import Work

DATABASE_FILE = 'database.db'


def init_database():
    if os.path.exists(DATABASE_FILE):
        return
    print('creating the database...')
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    create_table(cursor)
    import_data(cursor)
    conn.commit()
    conn.close()
    print('The database has been created')


def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table(cursor):
    create_composers_table(cursor)
    create_works_table(cursor)


def create_composers_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS composers(
               composer_id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               catalogue_source TEXT NOT NULL
        )
    ''')


def create_works_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS works(
            work_id INTEGER PRIMARY KEY AUTOINCREMENT,
            composer_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            creation_year INTEGER NOT NULL,
            detail_url TEXT NOT NULL,
            decade TEXT NOT NULL,
            FOREIGN KEY (composer_id) 
                REFERENCES composers (composer_id)
        )

    ''')


def import_data(cursor):
    works, _ = data_clean()
    if not works:
        return

    composer_ids = {}
    for composer_name in ['Carl Nielsen', 'Frederick Delius']:
        cid = insert_composer(composer_name, 'Official Catalogue', cursor)
        if cid:
            composer_ids[composer_name] = cid
            print(cid)
    for work in works:
        if 'Carl Nielsen' in work.composer:
            work.composer_id = composer_ids.get('Carl Nielsen')
        elif 'Frederick Delius' in work.composer:
            work.composer_id = composer_ids.get('Frederick Delius')
        if work.composer_id:
            insert_work(work, cursor)


def insert_composer(name: str, catalogue_source: str, cursor) -> int | None:
    cursor.execute('SELECT composer_id FROM composers WHERE name = ?', (name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute('''
        INSERT INTO composers (name, catalogue_source)
        VALUES (?, ?)
    ''', (name, catalogue_source))
    return cursor.lastrowid


def insert_work(work: Work, cursor):
    if not all([work.composer_id, work.title, work.genre, work.creation_year, work.detail_url, work.decade]):
        return None
    cursor.execute('''
        INSERT INTO works (composer_id, title, genre, creation_year, detail_url,decade)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (work.composer_id, work.title, work.genre, work.creation_year, work.detail_url, work.decade))


def get_all_works():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT w.*, c.name as composer 
            FROM works w
            JOIN composers c ON w.composer_id = c.composer_id
    ''')
    rows = cursor.fetchall()
    conn.close()
    all_works = []
    for row in rows:
        work = Work(
            work_id=row['work_id'],
            composer_id=row['composer_id'],
            title=row['title'],
            genre=row['genre'],
            creation_year=row['creation_year'],
            detail_url=row['detail_url'],
            composer=row['composer'],
            decade=row['decade']
        )
        all_works.append(work)
    return all_works


if __name__ == '__main__':
    init_database()
    get_all_works()
