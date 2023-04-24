import PySimpleGUI as sg
import sys
import os.path
import bibtexparser
import pyperclip

from pybtex.database.input import bibtex


class listentries:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return self.value

def repr_persons(persons):
    rl = []
    for person in persons:
        ps = " ".join(person.first_names + person.middle_names +
                person.last_names)
        rl.append(ps)

    return ", ".join(rl)


bibfilepath = ""
if len(sys.argv) >= 2:
    if os.path.isfile(sys.argv[1]):
        bibfilepath = sys.argv[1]


sg.theme("DarkBlue3")
sg.set_options(font=("Arial", 12))

# First the window layout in 2 columns

file_list_column = [
    [
        sg.Text("Bibtex file"),
        sg.Input(bibfilepath, size=(25, 1), enable_events=True, key="-FILE-"),
        sg.FileBrowse(),
        sg.Button("Read"),
    ],
    [
        sg.Listbox( values=[]
                  , enable_events=True
                  , size=(40, 20)
                  , key="-ENTRY LIST-"
                  )
    ],
]

# For now will only show the name of the file that was chosen
image_viewer_column = [
    [sg.Text("Choose an article from list on left:")],
    [sg.Text(size=(40, 1), key="-ID-"), sg.Button("Copy")],
    [
        sg.Multiline( default_text="\n"
                    , disabled=True
                    , enable_events=False
                    , size=(40, 20)
                    , key="-CONTENTS-"
                    )
    ],
]

# Full layout
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]

window = sg.Window("Bib Viewer", layout, finalize=True)
ID = ""

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "Read":
        window["-CONTENTS-"].update("")
        if not os.path.isfile(values["-FILE-"]):
            window["-ENTRY LIST-"].update("")
            continue
        #with open(values["-FILE-"]) as f:
        #    bib_database = bibtexparser.load(f)
        parser = bibtex.Parser()
        bib_data = parser.parse_file(values["-FILE-"])

        # create a list of indices in the entries list, and the titles of the
        # corresponding articles, so as to be able to display and select
        # articles in the entry list.
        articlelist = []
        #i = 0
        #while i < len(bib_database.entries):
        #    entry = bib_database.entries[i]
        #    articlelist.append(listentries(i, entry['title']))
        #    i += 1
        for key in bib_data.entries.keys():
            entry = bib_data.entries[key]
            articlelist.append(listentries(key, entry.fields['title']))

        window["-ENTRY LIST-"].update(articlelist)

    elif event == "-ENTRY LIST-":  # A file was chosen from the listbox
        # clear content multiline
        window["-CONTENTS-"].update("")
        #entry = bib_database.entries[values["-ENTRY LIST-"][0].key]
        print(values["-ENTRY LIST-"][0].key)
        entry = bib_data.entries[values["-ENTRY LIST-"][0].key]
        contentlist = []

        #for key in entry.keys():
        for key in entry.fields.keys():
            contentlist.append("{0}: {1}".format(key, entry.fields[key]))
            window["-CONTENTS-"].update(key + ":\n", font=('Arial', 14, 'bold'), append=True)
            #window["-CONTENTS-"].update(entry[key] + "\n\n", font=('Arial', 12), append=True)
            window["-CONTENTS-"].update(entry.fields[key] + "\n\n", font=('Arial', 12), append=True)
        for key in entry.persons.keys():
            contentlist.append("{0}: {1}".format(key, entry.persons[key]))
            window["-CONTENTS-"].update(key + ":\n", font=('Arial', 14, 'bold'), append=True)
            #window["-CONTENTS-"].update(entry[key] + "\n\n", font=('Arial', 12), append=True)
            window["-CONTENTS-"].update(repr_persons(entry.persons[key]) + "\n\n", font=('Arial', 12), append=True)

        #window["-ID-"].update(entry["ID"])
        window["-ID-"].update(values["-ENTRY LIST-"][0].key)
        #ID = entry["ID"]
        ID = values["-ENTRY LIST-"][0].key
    elif event == "Copy":
        if not ID == "":
            pyperclip.copy(ID)

#with open("outdump.bib", 'w') as f:
#    bibtexparser.dump(bib_database, f)
window.close()

