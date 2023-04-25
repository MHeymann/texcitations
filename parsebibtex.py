#! /usr/bin/python3

def parse_whitespace(f, c):
    while c.isspace():
        c = f.read(1)
    return f, c

def is_allowable_in_cite_key(c):
    if c.isalpha() or c.isnumeric() or c in ['-', '_', ":", "."]:
        return True
    else:
        return False

def parse_cite_key(f, c):
    if not is_allowable_in_cite_key(c):
        print(f"{c} is not allowable in cite_key")
        exit()

    cite_key = ""
    while is_allowable_in_cite_key(c):
        cite_key += c
        c = f.read(1)

    return cite_key, f, c


def parse_type(f, c):
    if not c == "@":
        print ("Type should be of the form '@<type>', instead, we got '{c}' as starting letter")
        exit()
    # skip over @
    c = f.read(1)

    if not c.isalpha():
        print ("Type should be of the form '@<type>', instead, we got '@{c}' as starting letters")
        exit()

    s = ""
    while c.isalpha():
        s += c
        c = f.read(1)
    f, c = parse_whitespace(f, c)
    return s.lower(), f, c

def parse_quote(f, c):
    qcontent =""

    if not c == "\"":
        print ("open quotes with '\"'")
        exit()

    c = f.read(1)

    while not c == "\"":
        if c.isspace():
            qcontent += " "
            f, c = parse_whitespace(f, c)
        elif c == "{":
            nbracket, f, c = parse_bracket(f, c)
            f, c = parse_whitespace(f, c)
            qcontent += "{" + nbracket + "}"
        else:
            qcontent += c
            c = f.read(1)

    #skip closing quotation sign
    c = f.read(1)

    f, c = parse_whitespace(f, c)

    return qcontent, f, c



def parse_bracket(f, c):
    f, c = parse_whitespace(f, c)
    bcontent =""

    if not c == "{":
        print ("open brackets with '{'")
        exit()

    c = f.read(1)

    while not c == "}":

        if c.isspace():
            bcontent += " "
            f, c = parse_whitespace(f, c)
        elif c == "{":
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


def parse_number(f, c):
    num = ""

    if not c.isnumeric():
        print(f"Numbers have to start with numerical characters, got '{c}' instead.")
        exit()

    while c.isnumeric():
        num += c
        c = f.read(1)

    return num, f, c

def parse_field(f, c):
    f, c = parse_whitespace(f, c)

    fname = ""
    while c.isalpha():
        fname += c
        c = f.read(1)
    fname = fname.lower()

    f, c = parse_whitespace(f, c)

    if not c == "=":
        print(f"expected '=', found '{c}'")
        exit()

    c = f.read(1)
    f, c = parse_whitespace(f, c)

    if c == "{":
        fvalue, f, c = parse_bracket(f,c)
    elif c == "\"":
        fvalue, f, c = parse_quote(f,c)
    else:
        fvalue , f, c = parse_number(f,c)

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

    key, f, c = parse_cite_key(f, c)
    #while c and not c.isspace() and not c == ",":
    #    key += c
    #    c = f.read(1)
    f, c = parse_whitespace(f, c)

    if not c == ",":
        print(f"Expected ',' after key, found '{c}'")
        exit()

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

def repr_entry(entry):
    s = f'@{entry["entry_type"]}{{{entry["cite_key"]},\n'

    l = []
    for k in entry["fields"].keys():
        l.append(f'  {k : <9} = {{{entry["fields"][k]}}},')
    for comm in entry["comments"]:
        l.insert(comm, "  %" + entry["comments"][comm])

    s += "\n".join(l)

    s += "\n}"
    return s

def parse_entry(f, c):
    if not c == "@":
        print ("Entries start with '@'")
        exit()

    entry_type, f, c = parse_type(f, c)

    f, c = parse_whitespace(f, c)

    if not c == "{":
        print (f"Entry body should start with '{{', got {c} instead")
        exit()

    key, fields, lcomments, f, c = parse_entry_body(f, c)

    return {
            "cite_key"   : key,
            "entry_type" : entry_type,
            "fields"     : fields,
            "comments"   : lcomments
            }, f, c

def bibtexlibrary_repr(bibtexlibrary):
    s = ""
    for e_type in bibtexlibrary:
        for cite_key in bibtexlibrary[e_type]:
            s += repr_entry(bibtexlibrary[e_type][cite_key])
            s += "\n\n"
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

            # xxx here
            entry, f, c = parse_entry(f, c)

            bibtexlibrary[entry["entry_type"]][entry["cite_key"]] = entry

            #print(repr_entry(entry))
            #print("")
    print(bibtexlibrary_repr(bibtexlibrary))

    return bibtexlibrary

parse_library("../bibliography.bib")
#parse_library("./bib.bib")
