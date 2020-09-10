"""
codequestion query shell module.
"""

from cmd import Cmd

from .query import Query

class Shell(Cmd):
    """
    codequestion query shell.
    """

    intro = "codequestion query shell"
    prompt = "(cqq) "
    embeddings = None
    db = None
    lang = None

    def preloop(self):
        # Load embeddings and questions.db
        self.embeddings, self.db = Query.load()

    def postloop(self):
        if self.db:
            self.db.close()

    def default(self, line):
        Query.query(self.embeddings, self.db, "%s %s" % (self.lang, line) if self.lang else line)

    def do_lang(self, lang):
        """
        Sets the default programming language for this session. All queries will have the language
        prepended to the query.

        Args:
            lang: language
        """

        self.lang = lang
        print("Set language to %s" % lang)

def main():
    """
    Shell execution loop.
    """

    Shell().cmdloop()

if __name__ == "__main__":
    main()
