"""
Filters a raw posts.xml file for matching results. Uses raw text processing to avoid overhead of parsing xml.
"""

import re

def parse(pattern, line):
    """
    Parses an int field and returns the value if found. Returns -1 if no value found.

    Args:
        pattern: regex pattern
        line: input line

    Return:
        field value
    """

    field = re.search(pattern, line)
    return int(field.group(1)) if field else -1

def run(infile, outfile):
    """
    Processes a raw Posts.xml file. The Posts dump is in Id order ascending.

    Args:
        infile: path to input file
        outfile: path to output file
    """

    print("Converting %s to %s" % (infile, outfile))

    # Set of answer ids
    ids = set()

    with open(infile) as xml:
        with open(outfile, "w") as output:
            # Write xml start
            output.write("<posts>\n")

            for line in xml:
                # PostTypeId = 1 (Question) with accepted answer.
                if "AcceptedAnswerId" in line:
                    # Parse answer id and score
                    answer = parse(r"AcceptedAnswerId=\"([0-9]+)\"", line)
                    score = parse(r"Score=\"([0-9]+)\"", line)

                    # Require a score of 10+.
                    if score >= 10:
                        # Add answer id to ids list
                        ids.add(answer)

                        # Write accepted line
                        output.write(line)

                # PostTypeId = 2 (Answer)
                elif "PostTypeId=\"2\"" in line:
                    # Parse post id
                    pid = parse(r"Id=\"([0-9]+)\"", line)

                    if pid in ids:
                        # Write output line and remove from ids list
                        output.write(line)
                        ids.remove(pid)

            # Write xml end
            output.write("</posts>\n")
