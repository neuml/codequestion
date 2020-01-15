"""
Converts a filtered posts xml file to a staging SQLite database for processing.
"""

import os
import xml.etree.cElementTree as etree
import sqlite3

# Questions schema
QUESTIONS = {
    'Id': 'INTEGER PRIMARY KEY',
    'AcceptedAnswerId': 'INTEGER',
    'CreationDate': 'DATETIME',
    'LastActivityDate': 'DATETIME',
    'Score': 'INTEGER',
    'ViewCount': 'INTEGER',
    'OwnerUserId': 'INTEGER',
    'OwnerDisplayName': 'TEXT',
    'Title': 'TEXT',
    'Tags': 'TEXT',
    'AnswerCount': 'INTEGER',
    'CommentCount': 'INTEGER',
    'FavoriteCount': 'INTEGER',
    'ClosedDate': 'DATETIME'
}

# Answers schema
ANSWERS = {
    'Id': 'INTEGER PRIMARY KEY',
    'ParentId': 'INTEGER',
    'CreationDate': 'DATETIME',
    'Score': 'INTEGER',
    'Body': 'TEXT',
    'OwnerUserId': 'INTEGER',
    'OwnerDisplayName': 'TEXT'
}

# SQL statements
CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {table} ({fields})"
INSERT_ROW = "INSERT INTO {table} ({columns}) VALUES ({values})"

def create(db, table, name):
    """
    Creates a SQLite table.

    Args:
        db: database connection
        table: table schema
        name: table name
    """

    columns = ['{0} {1}'.format(name, ctype) for name, ctype in table.items()]
    create = CREATE_TABLE.format(table=name, fields=", ".join(columns))

    # pylint: disable=W0703
    try:
        db.execute(create)
    except Exception as e:
        print(create)
        print("Failed to create table: " + e)

def xmlstream(xml):
    """
    Creates a xml stream for iterative parsing.

    Args:
        xml: input file

    Returns:
        context, root
    """

    # Parse the tree
    context = etree.iterparse(xml, events=("start", "end"))

    # turn it into an iterator
    context = iter(context)

    # get the root element
    _, root = next(context)

    return context, root

def insert(db, row):
    """
    Inserts row into database.

    Args:
        db: database connection
        row: row tuple
    """

    if "PostTypeId" in row.attrib:
        # PostType="1" - Question, PostType="2" - Answer
        table = QUESTIONS if row.attrib["PostTypeId"] == "1" else ANSWERS
        name = "questions" if row.attrib["PostTypeId"] == "1" else "answers"

        # Build insert prepared statement
        columns = [name for name, _ in table.items()]
        insert = INSERT_ROW.format(table=name,
                                   columns=", ".join(columns),
                                   values=("?, " * len(columns))[:-2])

        # Execute insert statement
        db.execute(insert, values(table, row, columns))

def values(table, row, columns):
    """
    Formats and converts row into database types based on table schema.

    Args:
        table: table schema
        row: row tuple
        columns: column names

    Returns:
        Database schema formatted row tuple
    """

    values = []
    for column in columns:
        # Get column value
        value = row.attrib[column] if column in row.attrib else None

        if table[column].startswith('INTEGER'):
            values.append(int(value) if value else 0)
        elif table[column] == 'BOOLEAN':
            values.append(1 if value == "TRUE" else 0)
        else:
            values.append(value)

    return values

def run(infile, dbfile):
    """
    Converts xml infile to SQLite dbfile.

    Args:
        infile: input xml file
        dbfile: output sqlite file
    """

    print("Converting %s to %s" % (infile, dbfile))

    # Delete existing file
    if os.path.exists(dbfile):
        os.remove(dbfile)

    # Create new database
    db = sqlite3.connect(dbfile)

    # Create database tables if necessary
    create(db, QUESTIONS, "questions")
    create(db, ANSWERS, "answers")

    count = 0
    with open(infile) as xml:
        context, root = xmlstream(xml)

        for event, row in context:
            if event == "end":
                # Execute insert statement
                insert(db, row)

                count += 1
                if count % 10000 == 0:
                    print("Inserted {} rows".format(count))

                # Free memory
                root.clear()

    print("Total rows inserted: {}".format(count))

    # Commit changes
    db.commit()
