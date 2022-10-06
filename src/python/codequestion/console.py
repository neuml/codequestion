"""
Console module
"""

from cmd import Cmd

from rich.console import Console as RichConsole

from .path import Path
from .search import Search
from .topics import Topics


class Console(Cmd):
    """
    codequestion console.
    """

    def __init__(self):
        """
        Creates a new codequestion console.
        """

        super().__init__()

        # Display configuration
        self.intro = "codequestion console"
        self.prompt = ">>> "
        self.console = RichConsole()

        # Search parameters
        self.search = None
        self.embeddings = None
        self.limit = 1

        # Topics action
        self.topics = None

        # Path traversal action
        self.path = None

    def preloop(self):
        """
        Loads initial configuration.
        """

        # Load query and embeddings
        self.search = Search()
        self.embeddings = self.search.embeddings

        # Load graph-based actions, if necessary
        if self.embeddings.graph:
            if self.embeddings.graph.topics:
                self.topics = Topics(self.embeddings)

            self.path = Path(self.embeddings)

    def default(self, line):
        """
        Default event loop.

        Args:
            line: command line
        """

        # pylint: disable=W0703
        try:
            command = line.lower()
            if command.startswith(".limit"):
                command = self.split(line)
                self.limit = int(command[1])
            elif command.startswith(".path") and self.path:
                command = self.split(line)
                start, end = command[1].split()
                self.path(int(start), int(end))
            elif command.startswith(".show"):
                command = self.split(line)
                self.search(uid=command[1])
            elif command.startswith(".topics") and self.topics:
                command = self.split(line)
                self.topics(command[1] if len(command) > 1 else None)
            else:
                # Search is default action
                self.search(line, self.limit)
        except Exception:
            self.console.print_exception()

    def do_help(self, arg):
        """
        Shows a help message.

        Args:
            arg: optional help message argument
        """

        commands = {
            ".limit": "(number)\t\tset the maximum number of query rows to return",
            ".path": "(start) (end)\tprints a semantic path between questions",
            ".show": "(id)\t\tprint question with specified id",
            ".topics": "(query)\t\tshows topics best matching query. if query is empty, top topics are shown",
        }

        if arg in commands:
            self.console.print(f"{arg} {commands[arg]}")
        else:
            for command, message in commands.items():
                self.console.print(f"{command} {message}")

            self.console.print("\nDefault mode runs a search query")

    def split(self, command, default=None):
        """
        Splits command by whitespace.

        Args:
            command: command line
            default: default command action

        Returns:
            command action
        """

        values = command.split(" ", 1)
        return values if len(values) > 1 else (command, default)


def main():
    """
    Console execution loop.
    """

    Console().cmdloop()


if __name__ == "__main__":
    main()
