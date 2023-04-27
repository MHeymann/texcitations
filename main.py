#! /usr/bin/python3

import PySimpleGUI as sg
import sys
import os.path
import parsebibtex
import pyperclip

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

def get_bibfilepath():
    bibfilepath = ""
    if len(sys.argv) >= 2:
        if os.path.isfile(sys.argv[1]):
            bibfilepath = sys.argv[1]
        else:
            print(sys.argv[1] + " is not a file")
    return bibfilepath


def get_layout(bibfilepath):
# The window layout in 2 columns
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
        [sg.Text(size=(40, 1), key="-ID-", enable_events=True), sg.Button("Copy")],
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
    return layout

def read_library(window, libpath):
    # Folder name was filled in, make a list of files in the folder
    window["-CONTENTS-"].update("")
    if not os.path.isfile(libpath):
        window["-ENTRY LIST-"].update("")
        return None

    bib_data = parsebibtex.parse_library(libpath)

    # create a list of indices in the entries list, and the titles of the
    # corresponding articles, so as to be able to display and select
    # articles in the entry list.
    articlelist = []
    for cite_key in bib_data:
        entry = bib_data[cite_key]
        articlelist.append(listentries(cite_key, "- " + entry["fields"]['title']))

    window["-ENTRY LIST-"].update(articlelist)
    return bib_data

def choose_entry(window, bib_data):
    # clear content multiline
    window["-CONTENTS-"].update("")
    entry = bib_data[values["-ENTRY LIST-"][0].key]
    contentlist = []

    for field in entry["fields"]:
        contentlist.append(f'{field}: \n{entry["fields"][field]}\n')
    if len(entry["comments"]) > 0:
        contentlist.append("comments:")
        for comment in entry["comments"]:
            contentlist.append("%" + entry["comments"][comment])


    window["-CONTENTS-"].update("\n".join(contentlist))

    window["-ID-"].update(values["-ENTRY LIST-"][0].key)
    ID = values["-ENTRY LIST-"][0].key
    return ID


if __name__ == "__main__":
    bibfilepath = get_bibfilepath()

    sg.theme("DarkBlue3")
    sg.set_options(font=("Arial", 12))
    layout = get_layout(bibfilepath)
    window = sg.Window("Bib Viewer", layout, finalize=True)
    ID = ""

    bib_data = read_library(window, bibfilepath)

    # Run the Event Loop
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == "Read":
            # read in the bibtex library
            bibfilepath = values["-FILE-"]
            bib_data = read_library(window, bibfilepath)
        elif event == "-ENTRY LIST-" and len(values["-ENTRY LIST-"]) > 0:
            # A file was chosen from the listbox
            ID = choose_entry(window, bib_data)
        elif event == "Copy":
            if not ID == "":
                pyperclip.copy(ID)

    if bib_data:
        with open("outdump.bib", 'w', encoding="utf8") as f:
            parsebibtex.dump(bib_data, f)
    window.close()


