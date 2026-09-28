import sqlite3
import pandas as pd
import re

"""
- handles input validation
- leading or trailing spaces in input
"""

db = 'test.db'


# info_table to keep track of columns datatypes and any constraints on columns
# to be called when app is first loaded
def create_info_table():
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS info_table (table_name, column_name, column_type)')

def validate_table_name(name):
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_ ]*', name):
        raise ValueError("Invalid table name")
    return name

def validate_column_name(name):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_ ]*', name):
        raise ValueError("Invalid column name")
    return name

def validate_columns_names(names):
    not_valid_names = []
    for name in names:
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_ ]*', name):
            not_valid_names.append(name)
    if len(not_valid_names)>0:
        raise ValueError(f"Invalid column names: {not_valid_names}")
    return

def create_collection(title,*columns):
    if (len(columns)==0):
        raise ValueError("No columns provided")
    title = title.strip()
    #validate title; raises error if not valid
    validate_table_name(title)
    cols = [arg.strip() for arg in columns]
    validate_columns_names(cols)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        #check if table exists
        res = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name = ?',(title,))
        table_exists = res.fetchone() is not None
        if table_exists:
            return(f"collection '{title}' already exists")
        else:
            cols = ",".join(f'"{x}"' for x in cols)
            cur.execute(f'CREATE TABLE "{title}" (id INTEGER PRIMARY KEY AUTOINCREMENT, {cols})')
            return(f"collection '{title}' created")

def save_collection_info(title,columns_details):
    title = title.strip()
    #validate title; raises error if not valid
    validate_table_name(title)
    # columns = headings['field']
    # types = headings['type']
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.executemany(
            f'INSERT INTO info_table (table_name, column_name, column_type) VALUES ("{title}",?,?) ',
            columns_details
        )

def delete_collection(title):
    title = title.strip()
    #validate title; raises error if not valid
    validate_table_name(title)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        #check if table exists
        res = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name = ?',(title,))
        table_exists = res.fetchone() is not None
        if table_exists:
            cur.execute(f'DROP table "{title}"')
            return f"{title} collection deleted"
        else:
            return f"{title} is NOT a collection"

def delete_collection_info(title):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM info_table WHERE table_name = ?',(title,))

def fetch_collection_details(title):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        res = cur.execute('SELECT column_name, column_type FROM info_table WHERE table_name = ?', (title,))
        return res.fetchall()

def fetch_all_collections_details():
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        res = cur.execute('SELECT DISTINCT table_name FROM info_table')
        titles = [title for (title, ) in res.fetchall()]

        out = {}
        for i in range(0,len(titles)):
            out[titles[i]] = [x for x in fetch_collection_details(titles[i])]
        return out

def fetch_from_collection(title,limit=-1,fields=None):
    title = title.strip()
    #validate title; raises error if not valid
    validate_table_name(title)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        #check if table exists
        # res = cur.execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name = ?',(title,))
        res = cur.execute(f'SELECT table_name FROM info_table WHERE table_name=?',(title,))
        table_exists = res.fetchone() is not None
        if table_exists:
            if fields is None:
                columns = '*'
            elif len(fields) == 0:
                columns = '*'
            else:
                columns = [x.strip() for x in fields]
                validate_columns_names(columns)
                columns = ','.join(f'"{x}"' if isinstance(x, str) else str(x) for x in columns)
            query = f'SELECT {columns} FROM "{title}" limit ?'
            res = cur.execute(query,(limit,))
            table_description = res.description
            column_names = [info[0] for info in table_description]
            out = pd.DataFrame(res.fetchall(),columns=column_names)
            # if 'id' in out.columns:
            #     out.drop(columns='id',inplace=True)
            return(out)
        else:
            return pd.DataFrame()

def add_to_collection(title,**kwargs):
    if(len(kwargs)==0):
        raise ValueError("No data provided")
    title = title.strip()
    #validate title; raises error if not valid
    validate_table_name(title)
    columns = [x.strip() for x in kwargs.keys()]
    #check for columns passed
    validate_columns_names(columns)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        #check if table exists
        res = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name = ?', (title,))
        table_exists = res.fetchone() is not None
        if table_exists:
            columns = ",".join(f'"{x}"' if isinstance(x, str) else str(x) for x in list(columns))
            values = list(kwargs.values())
            placeholder = ",".join(['?']*len(values))
            query = f'INSERT INTO "{title}" ({columns}) VALUES ({placeholder})'
            res = cur.execute(query,values)
            return f"Added to {title}"
        else:
            return f"table {title} does not exist"

#NOTE: first check for existing columns for same name - can use fetch_collection_details function for that
def add_columns_to_collection(title, *columns):
    if (len(columns)==0):
        raise ValueError("No columns provided")
    title = title.strip()
    #validate title; raises error if not valid
    validate_table_name(title)
    cols = [arg.strip() for arg in columns]
    validate_columns_names(cols)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        #check if table exists
        res = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name = ?',(title,))
        table_exists = res.fetchone() is not None
        if not table_exists:
            return(f"collection '{title}' does not exist")
        else:
            for col in cols:
                cur.execute(f'ALTER TABLE {title} ADD COLUMN "{col}"')
            return(f"columns added to '{title}'")

#NOTE: First check if column exists / can use fetch_collection_details for that
def remove_columns_from_collection(title, *columns):
    if (len(columns)==0):
        raise ValueError("No columns provided")
    title = title.strip()
    #validate title; raises error if not valid
    validate_table_name(title)
    cols = [arg.strip() for arg in columns]
    validate_columns_names(cols)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        #check if table exists
        res = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name = ?',(title,))
        table_exists = res.fetchone() is not None
        if not table_exists:
            return(f"collection '{title}' does not exist")
        else:
            for col in cols:
                cur.execute(f'ALTER TABLE {title} DROP COLUMN "{col}"')
            return(f"columns removed from '{title}'")

def add_multi_to_collection(title, data):
    if(len(data)==0):
        raise ValueError("No data provided")
    title = title.strip()
    #validate title; raises error if not valid
    validate_table_name(title)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        #check if table exists
        res = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name = ?', (title,))
        table_exists = res.fetchone() is not None
        if table_exists:
            for row in data:
                if not row:
                    continue
                columns = [x.strip() for x in row.keys()]
                #check for columns passed
                validate_columns_names(columns)
                columns = ",".join(f'"{x}"' if isinstance(x, str) else str(x) for x in list(columns))
                values = list(row.values())
                placeholder = ",".join(['?']*len(values))
                query = f'INSERT INTO "{title}" ({columns}) VALUES ({placeholder})'
                res = cur.execute(query,values)
            return f"Added to {title}"
        else:
            return f"table {title} does not exist"
    # for row in data:
    #     if not row:
    #         continue
    #     add_to_collection(title, **row)

def remove_from_collection_using_ids(title, ids):
    if(len(ids)==0):
        raise ValueError("No data provided")
    title = title.strip()
    #validate title; raises error if not valid
    validate_table_name(title)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        #check if table exists
        res = cur.execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name = ?',(title,))
        table_exists = res.fetchone() is not None
        if table_exists:
            ids = [(x,) for x in ids]
            res = cur.executemany(f'DELETE FROM {title} WHERE id=?',ids)
        else:
            return f"table {title} does not exist"

def edit_collection_using_ids(title, data):
    #Note: data is to be in form: {id:{col1:val1,..},..}
    
    if(len(data)==0):
        raise ValueError("No data provided")
    title = title.strip()
    #validate title; raises error if not valid
    validate_table_name(title)
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        #check if table exists
        res = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name = ?', (title,))
        table_exists = res.fetchone() is not None
        if table_exists:
            for id, kwargs in data.items():
                if not kwargs:
                    continue
                columns = [x.strip() for x in kwargs.keys()]
                validate_columns_names(columns)
                placeholder = ", ".join(f'"{k}" = "{v}"' for k,v in kwargs.items())
                query = f'UPDATE "{title}" SET {placeholder} WHERE id={id}'
                # print(query)
                res = cur.execute(query)
            return f"Added to {title}"
        else:
            return f"table {title} does not exist"
