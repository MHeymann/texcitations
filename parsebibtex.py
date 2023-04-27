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
            qcontent += "{" + nbracket + "}"
        else:
            qcontent += c
            c = f.read(1)

    #skip closing quotation sign
    c = f.read(1)

    f, c = parse_whitespace(f, c)

    return qcontent.strip(), f, c



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
            bcontent += "{" + nbracket + "}"
        else:
            bcontent += c
            c = f.read(1)

    #skip over closing bracket
    c = f.read(1)

    return bcontent.strip(), f, c


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
            fname, fvalue, f, c = parse_field(f,c)
            if fname == "author" or fname == "editor":
                fvalue = format_names(fvalue)
            fields[fname] = fvalue
        i += 1

    f, c = parse_whitespace(f, c)
    return key, fields, lcomments, f, c

def format_names(authors):
    author_list = []

    name = ""
    i = 0
    while i < len(authors) - 4:
        if authors[i] == "{":
            i, bracket = skip_bracket(authors, i)
            name += f'{{{bracket}}}'
        elif authors[i: i+5] == " and ":
            author_list.append(name)
            i += 5
            name = ""
        else:
            name += authors[i]
            i += 1
    name += authors[i:]
    author_list.append(name)


    formatted_names = []
    for author in author_list:
        if "," in author:
            formatted_names.append(author)
            continue
        names = []
        name = ""
        i = 0
        while i < len(author):
            if author[i] == "{":
                i, bracket = skip_bracket(author, i)
                name += f"{{{bracket}}}"
            elif author[i] == " ":
                names.append(name)
                name = ""
                i += 1
            else:
                name += author[i]
                i += 1
        names.append(name)
        #names = author.split(" ")
        if len(names) > 1:
            formatted_names.append("{surname}, {names}".format(surname=names[-1],
                names=" ".join(names[0:-1])))
        else:
            formatted_names.append(names[0])
    return " and ".join(formatted_names)

def skip_bracket(authors, i):
    if not authors[i] == "{":
        print ("open brackets with '{'")
        exit()

    i += 1

    cont = ""
    while not authors[i] == "}":
        if authors[i] == "{":
            i, bracket = skip_bracket(authors, i)
            cont += f"{{{bracket}}}"
        else:
            cont += authors[i]
            i += 1

    #skip over closing bracket
    i += 1

    return i, cont



def repr_entry(entry):
    s = f'@{entry["entry_type"]}{{{entry["cite_key"]},\n'

    field_order = [ "author", "editor"
                  , "title"
                  , "booktitle"
                  , "journal"
                  , "chapter", "pages"
                  , "publisher", "school", "institution"
                  , "year"
                  , "note"
                  , "doi", "url"
                  ]
    l = []
    for key in field_order:
        if not key in entry["fields"]:
            continue
        l.append(f'  {key : <9} = {{{entry["fields"][key]}}},')

    for k in entry["fields"]:
        if k in field_order:
            continue
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
    for cite_key in bibtexlibrary:
        s += repr_entry(bibtexlibrary[cite_key])
        s += "\n\n"
    return s

def dump(bibtexlibrary, f):
    f.write(bibtexlibrary_repr(bibtexlibrary))

def parse_library(fpath):
    bibtexlibrary = {}

    with open(fpath, encoding="utf8") as f:
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

            bibtexlibrary[entry["cite_key"]] = entry

    return bibtexlibrary


#if __name__ = "__main__":
#    bl = parse_library("../bibliography2/bibliography.bib")
#    print(bibtexlibrary_repr(bl))
