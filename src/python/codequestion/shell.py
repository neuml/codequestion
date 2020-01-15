from cmd import Cmd

from .query import Query

class Shell(Cmd):
    intro = "Codequestion query shell. Type queries into shell."
    prompt = "(cqq) "
    embeddings = None
    db = None

    def preloop(self):
        # Load embeddings and questions.db
        self.embeddings, self.db = Query.load()

    def postloop(self):
        if self.db:
            self.db.close()

    def default(self, line):
        Query.query(self.embeddings, self.db, line)

if __name__ == "__main__":
    Shell().cmdloop()
