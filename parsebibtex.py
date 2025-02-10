#! /usr/bin/python3

import re

standard_months = [ "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
field_order = [ "entrysubtype"
              , "author", "editor"
              , "title", "subtitle"
              , "booktitle", "booksubtitle"
              , "year", "month", "day", "date"
              , "yeardivision"
              , "journal", "journalname"
              , "volume"
              , "number"
              , "chapter", "pages"
              , "publisher", "school", "institution"
              , "note"
              , "doi", "url"
              , "keywords"
              , "abstract"
              ]


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
        elif c == "\\":
            c = f.read(1) # skip escape
            qcontent += f"\\{c}"
            c = f.read(1) # skip special character
        elif c == "{":
            nbraces, f, c = parse_braces(f, c)
            qcontent += "{" + nbraces + "}"
        else:
            qcontent += c
            c = f.read(1)

    #skip closing quotation sign
    c = f.read(1)

    f, c = parse_whitespace(f, c)

    return qcontent.strip(), f, c



def parse_braces(f, c):
    f, c = parse_whitespace(f, c)
    bcontent =""

    if not c == "{":
        print ("open braces with '{'")
        exit()

    c = f.read(1)

    while not c == "}":

        if c.isspace():
            bcontent += " "
            f, c = parse_whitespace(f, c)
        elif c == "\\":
            c = f.read(1) # skip escape
            bcontent += f"\\{c}"
            c = f.read(1) # skip special character
        elif c == "{":
            nbraces, f, c = parse_braces(f, c)
            bcontent += "{" + nbraces + "}"
        else:
            bcontent += c
            c = f.read(1)

    #skip over closing brace
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

def parse_string(f, c):
    s = ""

    if not c.isalpha():
        print(f"Strings have to start with alphabetic characters, got '{c}' instead.")
        exit()

    while c.isalpha():
        s += c
        c = f.read(1)

    return s, f, c


def parse_field(f, c):
    f, c = parse_whitespace(f, c)

    fname = ""
    while c.isalpha():
        fname += c
        c = f.read(1)
    fname = fname.lower()

    f, c = parse_whitespace(f, c)

    if not c == "=":
        print(f"expected '=', found '{c}' for {fname}")
        exit()

    c = f.read(1)
    f, c = parse_whitespace(f, c)

    if c == "{":
        fvalue, f, c = parse_braces(f,c)
    elif c == "\"":
        fvalue, f, c = parse_quote(f,c)
    elif c.isalpha:
        fvalue , f, c = parse_string(f,c)
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

def format_month(month):
    if month.lower() in standard_months:
        return month.lower()
    elif month.isdigit():
        imonth = int(month) - 1
        return standard_months[imonth]
    else:
        for m in standard_months:
            if m in month.lower():
                return m
    print(f"Warning: {month} is a nonstandard  representation of a month")
    return month



def parse_entry_body(f, c):

    if not c == "{":
        print(f"Expected body start with '{'{'}', found '{c}'")
    c = f.read(1)
    f, c = parse_whitespace(f, c)

    key, f, c = parse_cite_key(f, c)
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
            elif fname == "month":
                fvalue = format_month(fvalue)

            fields[fname] = fvalue
        i += 1

    f, c = parse_whitespace(f, c)
    return key, fields, lcomments, f, c

def get_list_of_authors(authors):
    author_list = []
    name = ""
    i = 0
    while i < len(authors) - 4:
        if authors[i] == "\\":
            i += 1
            name += "\\" + authors[i]
            i += 1
        elif authors[i] == "{":
            i, braces = skip_braces(authors, i)
            name += f'{{{braces}}}'
        elif authors[i: i+5] == " and ":
            author_list.append(name)
            i += 5
            name = ""
        else:
            name += authors[i]
            i += 1
    name += authors[i:]
    author_list.append(name)

    return author_list

def get_names_surname(author):
    i = 0
    while i < len(author):
        if author[i] == "\\":
            i += 1
            i += 1
        elif author[i] == "{":
            i, braces = skip_braces(author, i)
        elif author[i] == ",":
            author = author[0:i] + "\n" + author[i+1:]
            #author[i] = "\n"
            i += 1
        elif author[i] == "\n":
            # this should never happen, actually
            #author[i] = " "
            author = author[0:i] + " " + author[i+1:]
            i += 1
        else:
            i += 1
    t_auth = author.split("\n")
    if len(t_auth) == 2:
        surname = t_auth[0]
        names = split_names_on_space(t_auth[1].strip())
    elif len(t_auth) == 1:
        i = 0
        names = split_names_on_space(author)
        surname = names[-1]
        names = names[0:-1]
    else:
        print (f"badly formed author format: {author}")
        print(t_auth)
        print(len(t_auth))
        exit()

    return names, surname

def split_names_on_space(author):
    i = 0
    names = []
    name = ""
    while i < len(author):
        if author[i] == "\\":
            i += 1
            name += "\\" + author[i]
            i += 1
        elif author[i] == "{":
            i, braces = skip_braces(author, i)
            name += f"{{{braces}}}"
        elif author[i] == " ":
            names.append(name)
            name = ""
            i += 1
        else:
            name += author[i]
            i += 1
    names.append(name)
    return names



def format_names(authors):
    author_list = get_list_of_authors(authors)

    formatted_names = []
    for author in author_list:
        names, surname = get_names_surname(author)
        if len(names) > 0:
            formatted_names.append("{surname}, {names}".format(surname=surname,
                names=" ".join(names)))
        else:
            formatted_names.append(surname)
    return " and ".join(formatted_names)

def skip_braces(authors, i):
    if not authors[i] == "{":
        print ("open braces with '{'")
        exit()

    i += 1

    cont = ""
    while not authors[i] == "}":
        if authors[i] == "{":
            i, braces = skip_braces(authors, i)
            cont += f"{{{braces}}}"
        else:
            cont += authors[i]
            i += 1

    #skip over closing brace
    i += 1

    return i, cont

def field_repr(fname, fvalue):
    if fname == "month" and fvalue in standard_months:
        return f'  {fname : <9} = {fvalue},'
    else:
        return f'  {fname : <9} = {{{fvalue}}},'

def entry_repr(entry):
    s = f'@{entry["entry_type"]}{{{entry["cite_key"]},\n'

    l = []
    for key in field_order:
        if not key in entry["fields"]:
            continue
        l.append(field_repr(key, entry["fields"][key]))

    for k in sorted(entry["fields"].keys()):
        if k in field_order:
            continue
        l.append(field_repr(k, entry["fields"][k]))
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

    cite_key, fields, lcomments, f, c = parse_entry_body(f, c)
    ordered_fields = {}
    for k in field_order:
        if not k in fields:
            continue
        ordered_fields[k] = fields[k]
    for k in fields:
        if k in k in field_order:
            continue
        ordered_fields[k] = fields[k]


    if "title" not in fields:
        print(cite_key, "contains no title!")

    return {
            "cite_key"   : cite_key,
            "entry_type" : entry_type,
            "fields"     : ordered_fields,
            "comments"   : lcomments
            }, f, c

def bibtexlibrary_repr(bibtexlibrary):
    s = ""
    for cite_key in bibtexlibrary:
        s += entry_repr(bibtexlibrary[cite_key])
        s += "\n\n"
    return s

def dump(bibtexlibrary, f):
    f.write(bibtexlibrary_repr(bibtexlibrary))

def entry_compare_key(a):
    regex = re.compile('[^a-zA-Z\d\s:]')
    if "author" in a[1]["fields"]:
        auth = regex.sub('', a[1]["fields"]["author"])
    elif "editor" in a[1]["fields"]:
        auth = regex.sub('', a[1]["fields"]["editor"])
    else:
        auth = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    if "year" in a[1]["fields"]:
        year = a[1]["fields"]["year"]
    elif "date" in a[1]["fields"]:
        year = a[1]["fields"]["date"][:4]
    else:
        year = "1800"
    if "title" in a[1]["fields"]:
        title = regex.sub('', a[1]["fields"]["title"])
    else:
        print("title-less bibtex-entry?")
        title = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    return (auth, year, title)


def sort_library(biblib):
    return dict(sorted(biblib.items(), key=entry_compare_key))


def parse_library(f):
    c = f.read(1)
    f, c = parse_whitespace(f, c)
    bibtexlibrary = {}
    while c:
        # get to start of entry
        while c and not c == "@":
            c = f.read(1)
        if not c:
            break

        # xxx here
        entry, f, c = parse_entry(f, c)

        if entry["cite_key"] in bibtexlibrary:
            print(entry["cite_key"], "is a duplicate.")
            exit()
        bibtexlibrary[entry["cite_key"]] = entry
    return sort_library(bibtexlibrary)



def read_library(fpath):
    bibtexlibrary = {}

    with open(fpath, encoding="utf8") as f:
        bibtexlibrary = parse_library(f)

    return bibtexlibrary


#if __name__ = "__main__":
#    bl = parse_library("../bibliography2/bibliography.bib")
#    print(bibtexlibrary_repr(bl))
