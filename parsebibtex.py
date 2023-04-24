

def parse_whitespace(f, c):
    while c.isspace():
        c = f.read(1)
    return f, c

def parse_key(f, c):
    pass

def parse_type(f, c):
    f, c = parse_whitespace(f, c)
    s = ""
    while c.isalpha():
        s += c
        c = f.read(1)
    f, c = parse_whitespace(f, c)
    return s.lower(), f, c

def parse_bracket(f, c):
    f, c = parse_whitespace(f, c)
    bcontent =""

    if not c == "{":
        print ("open brackets with '{'")
        exit()

    c = f.read(1)

    while not c == "}":

        if c == "{":
            nbracket, f, c = parse_bracket(f, c)
            f, c = parse_whitespace(f, c)
            bcontent += "{" + nbracket + "}"
        else:
            bcontent += c
            c = f.read(1)

    #skip closing bracket
    c = f.read(1)

    f, c = parse_whitespace(f, c)

    return bcontent, f, c



def parse_field(f, c):
    f, c = parse_whitespace(f, c)

    fname = ""
    while c.isalpha():
        fname += c
        c = f.read(1)

    f, c = parse_whitespace(f, c)

    if not c == "=":
        print(f"expected '=', found '{c}'")
        exit()

    c = f.read(1)
    f, c = parse_whitespace(f, c)

    fvalue, f, c = parse_bracket(f,c)

    if c == ",":
        c = f.read(1)

    f, c = parse_whitespace(f, c)

    return fname, fvalue, f, c

def parse_line_comment(f, c):
    if not c == "%":
        print(f"line comment expected to start with '%', found {c}")
        exit()

    c = f.read(1)
    lcomment = ""
    while not c == "\n":
        lcomment += c
        c = f.read(1)

    f, c = parse_whitespace(f, c)

    return lcomment, f, c


def parse_entry_body(f, c):

    if not c == "{":
        print(f"Expected body start with '{'{'}', found '{c}'")
    c = f.read(1)
    f, c = parse_whitespace(f, c)

    key = ""
    while c and not c.isspace() and not c == ",":
        key += c
        c = f.read(1)
    f, c = parse_whitespace(f, c)

    if not c == ",":
        print(f"Expected ',' after key, found '{c}'")

    c = f.read(1)
    f, c = parse_whitespace(f, c)

    fields = {}
    lcomments = {}
    i = 0
    while not c == "}":
        if c == "%":
            lcomment, f, c = parse_line_comment(f, c)
            lcomments[i] = lcomment
        else:
            fname, v, f, c = parse_field(f,c)
            fields[fname] = v
        i += 1

    f, c = parse_whitespace(f, c)
    return key, fields, lcomments, f, c

def repr_entry(entry_type, key, fields, lcomments):
    s = f"@{entry_type}{{{key},\n"

    l = []
    for k in fields.keys():
        l.append(f"  {k : <9} = {{{fields[k]}}}")
    s += ",\n".join(l)

    s += "\n}"
    return s


def parse_library(fpath):
    bibtexlibrary = {
        "article" : {},
        "book" : {},
        "booklet" : {},
        "conference" : {},
        "inbook" : {},
        "incollection" : {},
        "inproceedings" : {},
        "manual" : {},
        "mastersthesis" : {},
        "misc" : {},
        "phdthesis" : {},
        "proceedings" : {},
        "techreport" : {},
        "unpublished" : {}
        }

    with open(fpath) as f:
        c = f.read(1)
        f, c = parse_whitespace(f, c)
        while c:
            # get to start of entry
            while c and not c == "@":
                c = f.read(1)
            if not c:
                break
            c = f.read(1)

            entry_type, f, c = parse_type(f, c)

            key, fields, lcomments, f, c = parse_entry_body(f, c)

            print(repr_entry(entry_type, key, fields, lcomments))
            print("")

    return bibtexlibrary

parse_library("biblib.bib")
