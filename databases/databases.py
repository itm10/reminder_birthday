import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


def create_lavozim():
    con = connection()
    cur = con.cursor()
    cur.execute('''
        create table if not exists lavozimlar(
            id serial primary key,
            lavozim varchar(30)
        )
    ''')
    con.commit()
    con.close()


def insert_lavozim(data: dict):
    con = connection()
    cur = con.cursor()
    cur.execute('''
            insert into lavozimlar(lavozim)
            values (%s)
            returning id
        ''', (*data.values(),))
    inserted_id = cur.fetchone()[0]
    con.commit()
    con.close()
    return inserted_id


def create_table_email():
    con = connection()
    cur = con.cursor()
    cur.execute('''
        create table if not exists users(
            id serial primary key,
            first_name varchar(30),
            last_name varchar(30),
            lavozim integer references lavozimlar(id),
            birth_day DATE,
            image text,
            chat_id integer null 
        )
    ''')
    con.commit()
    con.close()


def insert_data(data: dict):
    con = connection()
    cur = con.cursor()
    cur.execute('''
            insert into users(first_name, last_name, lavozim, birth_day, image, chat_id)
            values (%s, %s, %s, %s, %s, %s)
            returning id
        ''', (*data.values(),))
    inserted_id = cur.fetchone()[0]
    con.commit()
    con.close()
    return inserted_id


def get_user_admin():
    con = connection()
    cur = con.cursor()
    cur.execute('''
            SELECT * FROM users
            WHERE lavozim IN (SELECT id FROM lavozimlar WHERE lavozim = 'admin')
    ''')
    emails = cur.fetchall()
    con.close()
    return emails


def check_time():
    con = connection()
    cur = con.cursor()
    cur.execute('''
                SELECT u.first_name, u.last_name, u.image, l.lavozim 
                FROM users u
                INNER JOIN lavozimlar l ON l.id = u.lavozim
                WHERE EXTRACT(MONTH FROM u.birth_day) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(DAY FROM u.birth_day) = EXTRACT(DAY FROM CURRENT_DATE)
        ''')
    rows = cur.fetchall()
    con.close()

    result = [{'first_name': row[0], 'last_name': row[1], 'image': row[2], 'lavozim': row[3]} for row in rows]
    return result