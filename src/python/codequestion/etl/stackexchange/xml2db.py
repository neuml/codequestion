"""
XML2DB module
"""

import os
import xml.etree.cElementTree as etree
import sqlite3


class XML2DB:
    """
    Converts a filtered posts xml file to a staging SQLite database for processing.
    """

    # Questions schema
    QUESTIONS = {
        "Id": "INTEGER PRIMARY KEY",
        "AcceptedAnswerId": "INTEGER",
        "CreationDate": "DATETIME",
        "LastActivityDate": "DATETIME",
        "Score": "INTEGER",
        "ViewCount": "INTEGER",
        "OwnerUserId": "INTEGER",
        "OwnerDisplayName": "TEXT",
        "Title": "TEXT",
        "Tags": "TEXT",
        "AnswerCount": "INTEGER",
        "CommentCount": "INTEGER",
        "FavoriteCount": "INTEGER",
        "ClosedDate": "DATETIME",
    }

    # Answers schema
    ANSWERS = {
        "Id": "INTEGER PRIMARY KEY",
        "ParentId": "INTEGER",
        "CreationDate": "DATETIME",
        "Score": "INTEGER",
        "Body": "TEXT",
        "OwnerUserId": "INTEGER",
        "OwnerDisplayName": "TEXT",
    }

    # SQL statements
    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {table} ({fields})"
    INSERT_ROW = "INSERT INTO {table} ({columns}) VALUES ({values})"

    def __call__(self, infile, dbfile):
        """
        Converts xml infile to SQLite dbfile.

        Args:
            infile: input xml file
            dbfile: output sqlite file
        """

        print(f"Converting {infile} to {dbfile}")

        # Delete existing file
        if os.path.exists(dbfile):
            os.remove(dbfile)

        # Create new database
        db = sqlite3.connect(dbfile)

        # Create database tables if necessary
        self.create(db, XML2DB.QUESTIONS, "questions")
        self.create(db, XML2DB.ANSWERS, "answers")

        count = 0
        with open(infile, encoding="utf-8") as xml:
            context, root = self.xmlstream(xml)

            for event, row in context:
                if event == "end":
                    # Execute insert statement
                    self.insert(db, row)

                    count += 1
                    if count % 10000 == 0:
                        print(f"Inserted {count} rows")

                    # Free memory
                    root.clear()

        print(f"Total rows inserted: {count}")

        # Commit changes
        db.commit()

    def create(self, db, table, name):
        """
        Creates a SQLite table.

        Args:
            db: database connection
            table: table schema
            name: table name
        """

        columns = [f"{name} {ctype}" for name, ctype in table.items()]
        create = XML2DB.CREATE_TABLE.format(table=name, fields=", ".join(columns))

        # pylint: disable=W0703
        try:
            db.execute(create)
        except Exception as e:
            print(create)
            print("Failed to create table: " + e)

    def xmlstream(self, xml):
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

    def insert(self, db, row):
        """
        Inserts row into database.

        Args:
            db: database connection
            row: row tuple
        """

        if "PostTypeId" in row.attrib:
            # PostType="1" - Question, PostType="2" - Answer
            table = (
                XML2DB.QUESTIONS if row.attrib["PostTypeId"] == "1" else XML2DB.ANSWERS
            )
            name = "questions" if row.attrib["PostTypeId"] == "1" else "answers"

            # Build insert prepared statement
            columns = [name for name, _ in table.items()]
            insert = XML2DB.INSERT_ROW.format(
                table=name,
                columns=", ".join(columns),
                values=("?, " * len(columns))[:-2],
            )

            # Execute insert statement
            db.execute(insert, self.values(table, row, columns))

    def values(self, table, row, columns):
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

            if table[column].startswith("INTEGER"):
                values.append(int(value) if value else 0)
            elif table[column] == "BOOLEAN":
                values.append(1 if value == "TRUE" else 0)
            else:
                values.append(value)

        return values
