"""
DB2QA module
"""

import os
import re
import sqlite3


class DB2QA:
    """
    Converts multiple staging SQLite database (questions, answers in separate tables per source) into a consolidated SQLite database
    with a single questions table.
    """

    # Questions schema
    QUESTIONS = {
        "Id": "INTEGER PRIMARY KEY",
        "Source": "TEXT",
        "SourceId": "INTEGER",
        "Date": "DATETIME",
        "Tags": "TEXT",
        "Question": "TEXT",
        "QuestionUser": "TEXT",
        "Answer": "TEXT",
        "AnswerUser": "TEXT",
        "Reference": "TEXT",
    }

    # List of sources
    SOURCES = {
        "ai": "https://ai.stackexchange.com",
        "android": "https://android.stackexchange.com",
        "apple": "https://apple.stackexchange.com",
        "arduino": "https://arduino.stackexchange.com",
        "askubuntu": "https://askubuntu.com",
        "avp": "https://avp.stackexchange.com",
        "codereview": "https://codereview.stackexchange.com",
        "cs": "https://cs.stackexchange.com",
        "datascience": "http://datascience.stackexchange.com",
        "dba": "https://dba.stackexchange.com",
        "devops": "https://devops.stackexchange.com",
        "dsp": "https://dsp.stackexchange.com",
        "raspberrypi": "https://raspberrypi.stackexchange.com",
        "reverseengineering": "https://reverseengineering.stackexchange.com",
        "scicomp": "https://scicomp.stackexchange.com",
        "security": "https://security.stackexchange.com",
        "serverfault": "https://serverfault.com",
        "stackoverflow": "https://stackoverflow.com",
        "stats": "https://stats.stackexchange.com",
        "superuser": "https://superuser.com",
        "unix": "https://unix.stackexchange.com",
        "vi": "https://vi.stackexchange.com",
        "wordpress": "https://wordpress.stackexchange.com",
    }

    # SQL statements
    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {table} ({fields})"
    INSERT_ROW = "INSERT INTO {table} ({columns}) VALUES ({values})"
    CREATE_SOURCE_INDEX = "CREATE INDEX source ON questions(Source, SourceId)"
    CREATE_TEXT_INDEX = "CREATE VIRTUAL TABLE search USING fts5(Id, Question, Tags)"
    INSERT_TEXT_ROWS = "INSERT INTO search SELECT Id, Question, Tags from questions"

    def __call__(self, databases, qafile):
        """
        Executes a run to convert a list of databases to a single consolidated questions db file.

        Args:
            databases: paths to input databases
            qafile: output database path
        """

        print(f"Converting {databases} to {qafile}")

        # Delete existing file
        if os.path.exists(qafile):
            os.remove(qafile)

        # Create output database
        qa = sqlite3.connect(qafile)

        # Create questions table
        self.create(qa, DB2QA.QUESTIONS, "questions")

        # Row index
        index = 0

        for dbfile in databases:
            print("Processing " + dbfile)

            # Create source name
            source = os.path.splitext(os.path.basename(dbfile))[0].lower()

            # Input database
            db = sqlite3.connect(dbfile)
            cur = db.cursor()

            cur.execute(
                "SELECT Id, AcceptedAnswerId, OwnerUserId, OwnerDisplayName, LastActivityDate, Title, Tags FROM questions"
            )

            # Need to select all rows to allow execution of insert statements
            for question in cur.fetchall():
                # Find accepted answer
                answer = self.find(question, cur)
                if answer:
                    # Combine into single question row
                    self.insert(qa, index, source, question, answer)

                    index += 1
                    if index % 10000 == 0:
                        print(f"Inserted {index} rows")

            db.close()

        print(f"Total rows inserted: {index}")

        # Create indices
        for statement in [
            DB2QA.CREATE_SOURCE_INDEX,
            DB2QA.CREATE_TEXT_INDEX,
            DB2QA.INSERT_TEXT_ROWS,
        ]:
            qa.execute(statement)

        # Commit changes and close
        qa.commit()
        qa.close()

    def create(self, db, table, name):
        """
        Creates a SQLite table.

        Args:
            db: database connection
            table: table schema
            name: table name
        """

        columns = [f"{name} {ctype}" for name, ctype in table.items()]
        create = DB2QA.CREATE_TABLE.format(table=name, fields=", ".join(columns))

        # pylint: disable=W0703
        try:
            db.execute(create)
        except Exception as e:
            print(create)
            print("Failed to create table: " + e)

    def find(self, question, cur):
        """
        Finds a corresponding answer for the input question.

        Args:
            question: input question row
            cur: database cursor

        Returns:
            Answer row if found, None otherwise
        """

        # Query for accepted answer
        cur.execute(
            "SELECT Body, OwnerUserId, OwnerDisplayName from answers where Id = ?",
            [question[1]],
        )
        answer = cur.fetchone()

        if answer and answer[0]:
            # Check if answer has a message body
            return answer

        return None

    def insert(self, db, index, source, question, answer):
        """
        Builds and inserts a consolidated question.

        Args:
            db: database connection
            index: row index
            source: question source
            question: question row
            answer: answer row
        """

        table = DB2QA.QUESTIONS

        # Build insert prepared statement
        columns = [name for name, _ in table.items()]
        insert = DB2QA.INSERT_ROW.format(
            table="questions",
            columns=", ".join(columns),
            values=("?, " * len(columns))[:-2],
        )

        # Build row of insert values
        row = self.build(index, source, question, answer)

        # Execute insert statement
        db.execute(insert, self.values(table, row, columns))

    def build(self, index, source, question, answer):
        """
        Builds a consolidated question row.

        Args:
            index: row index
            source: question source
            question: question row
            answer: answer row

        Returns:
            row tuple
        """

        # Parse tags into list of tags
        tags = re.sub(r"[<>]", " ", question[6]).split() if question[6] else None

        # Get user display name, fallback to user id
        quser = question[3] if question[3] else str(question[2])
        auser = answer[2] if answer[2] else str(answer[1])

        # Create URL reference
        reference = f"{DB2QA.SOURCES[source]}/questions/{question[0]}"

        # Id, Source, SourceId, Date, Tags, Question, QuestionUser, Answer, AnswerUser, Reference
        return (
            index,
            source,
            question[0],
            question[4],
            " ".join(tags),
            question[5],
            quser,
            answer[0],
            auser,
            reference,
        )

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
        for x, column in enumerate(columns):
            # Get value
            value = row[x]

            if table[column].startswith("INTEGER"):
                values.append(int(value) if value else 0)
            elif table[column] == "BOOLEAN":
                values.append(1 if value == "TRUE" else 0)
            else:
                values.append(value)

        return values
