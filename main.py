import PySimpleGUI as sg
import os.path
import bibtexparser
import pyperclip

class listentries:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return self.value


sg.theme("DarkBlue3")
sg.set_options(font=("Arial", 12))

# First the window layout in 2 columns

file_list_column = [
    [
        sg.Text("Bibtex file"),
        sg.In(size=(25, 1), enable_events=True, key="-FILE-"),
        sg.FileBrowse(),
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
    if event == "-FILE-":
        with open(values["-FILE-"]) as f:
            bib_database = bibtexparser.load(f)

        # create a list of indices in the entries list, and the titles of the
        # corresponding articles, so as to be able to display and select
        # articles in the entry list.
        articlelist = []
        i = 0
        while i < len(bib_database.entries):
            entry = bib_database.entries[i]
            articlelist.append(listentries(i, entry['title']))
            i += 1

        window["-ENTRY LIST-"].update(articlelist)

    elif event == "-ENTRY LIST-":  # A file was chosen from the listbox
        # clear content multiline
        window["-CONTENTS-"].update("")
        entry = bib_database.entries[values["-ENTRY LIST-"][0].key]
        contentlist = []

        for key in entry.keys():
            contentlist.append("{0}: {1}".format(key, entry[key]))
            window["-CONTENTS-"].update(key + ":\n", font=('Arial', 14, 'bold'), append=True)
            window["-CONTENTS-"].update(entry[key] + "\n\n", font=('Arial', 12), append=True)
        window["-ID-"].update(entry["ID"])
        ID = entry["ID"]
    elif event == "Copy":
        if not ID == "":
            pyperclip.copy(ID)

with open("outdump.bib", 'w') as f:
    bibtexparser.dump(bib_database, f)
window.close()

