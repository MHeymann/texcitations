#! /usr/bin/python3

import PySimpleGUI as sg
import sys
import os.path
import parsebibtex
import pyperclip
import io

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
        ],
        [
            sg.FileBrowse(target="-FILE-"),
            sg.Button("Read"),
            sg.Button("Insert"),
            sg.Button("Save"),
        ],
        [
            sg.Listbox( values=[]
                      , enable_events=True
                      , size=(40, 20)
                      , key="-ENTRY LIST-"
                      )
        ],
        [
            sg.Text("Search"),
            sg.Input("", size=(25, 1), enable_events=True, key="-SEARCH-"),
        ],
    ]

    # For now will only show the name of the file that was chosen
    image_viewer_column = [
        [sg.Text("Choose an article from list on left:")],
        [sg.Text(size=(40, 1), key="-ID-", enable_events=True), sg.Button("Copy"), sg.Button("Edit")],
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

    bib_data = parsebibtex.read_library(libpath)

    # create a list of indices in the entries list, and the titles of the
    # corresponding articles, so as to be able to display and select
    # articles in the entry list.
    articlelist = []
    for cite_key in bib_data:
        entry = bib_data[cite_key]
        if "title" not in entry["fields"]:
            print (cite_key, "has no 'title' field.")
            exit()
        articlelist.append(listentries(cite_key, "- " + entry["fields"]['title']))

    window["-ENTRY LIST-"].update(articlelist)
    return bib_data

def searchterm_in_list(searchterm, l):
    for s in l:
        if searchterm in l[s].lower():
            return True
    return False

def search_for_occurance(window, searchterm, bib_data):

    searchterm = searchterm.lower()
    window["-CONTENTS-"].update("")
    articlelist = []
    for cite_key in bib_data:
        entry = bib_data[cite_key]
        for field in entry["fields"]:
            if searchterm in entry["fields"][field].lower() or \
                    searchterm in field or \
                    searchterm in entry["cite_key"].lower() or \
                    searchterm in entry["entry_type"].lower() or \
                    searchterm_in_list(searchterm, entry["comments"]):
                articlelist.append(listentries(cite_key, "- " + entry["fields"]['title']))
                break

    window["-ENTRY LIST-"].update(articlelist)

def choose_entry(window, entry):
    # clear content multiline
    window["-CONTENTS-"].update("")
    contentlist = [f'Entry Type: {entry["entry_type"]}\n']

    for field in entry["fields"]:
        contentlist.append(f'{field}: \n{entry["fields"][field]}\n')
    if len(entry["comments"]) > 0:
        contentlist.append("comments:")
        for comment in entry["comments"]:
            contentlist.append("%" + entry["comments"][comment])


    window["-CONTENTS-"].update("\n".join(contentlist))

    window["-ID-"].update(entry["cite_key"])
    ID = values["-ENTRY LIST-"][0].key
    return ID

def write_bibtex_to_file(bib_data, path):
    print(f"write to {path}")

    if bib_data:
        with open(path, 'w', encoding="utf8") as f:
            parsebibtex.dump(bib_data, f)
    else:
        sg.popup("Warning: could not save - no library read in.")


def popup_get_Mtext(message, default_text="", size=(50, 15), title=None, icon=None, keep_on_top=False):
    layout = [
        [sg.Text(message, auto_size_text=True)],
        [sg.MLine(default_text=default_text, size=size, key='-INPUT-')],
        [sg.Button('Submit', size=(8, 1), bind_return_key=True), sg.Button('Cancel', size=(8, 1))]
    ]

    iwindow = sg.Window(title=title or message,
                       layout=layout,
                       icon=icon,
                       keep_on_top=keep_on_top,
                       finalize=True,
                       modal=True
                       )
    button, values = iwindow.read()
    iwindow.close()
    del iwindow
    if button != 'Submit':
        return None
    else:
        path = values['-INPUT-']
        return path

if __name__ == "__main__":
    saved = False
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
            if saved:
                pass
            elif sg.popup_yes_no(f'Do you want to save to {bibfilepath}?') == "Yes":
                write_bibtex_to_file(bib_data, bibfilepath)
            elif sg.popup_yes_no(f'Do you want to save to a different file?') == "Yes":
                bibfilepath = sg.popup_get_file("Please provide a file path to save to", save_as=True)
                write_bibtex_to_file(bib_data, bibfilepath)
            break
        if event == "Read":
            # read in the bibtex library
            #bibfilepath = values["-FILE-"]
            bib_data = read_library(window, bibfilepath)
        elif event == "-FILE-":
            bibfilepath = values["-FILE-"]
        elif event == "Insert":
            new_entry_text = popup_get_Mtext("Please enter the bibtex code for the entry to be added below", title="Insert",size=(50,10))
            f = io.StringIO(new_entry_text)
            new_lib = parsebibtex.parse_library(f)
            cite_key_collide = False
            for cite_key in new_lib:
                if cite_key in bib_data:
                    sg.popup(f"{cite_key} is a duplicate, please enter with different cite_key")
                    cite_key_collide = True
            if not cite_key_collide:
                for cite_key in new_lib:
                    bib_data[cite_key] = new_lib[cite_key]
            search_for_occurance(window, values["-SEARCH-"], bib_data)
        elif event == "Save":
            if sg.popup_yes_no(f'Do you want to save to {bibfilepath}?') == "Yes":
                write_bibtex_to_file(bib_data, bibfilepath)
                saved = True
            else:
                custompath = sg.popup_get_file("Please provide a file path to save to", save_as=True)
                if custompath:
                    write_bibtex_to_file(bib_data, custompath)
                    saved = True
                else:
                    sg.popup("Not saving.")
        elif event == "-ENTRY LIST-" and len(values["-ENTRY LIST-"]) > 0:
            # A file was chosen from the listbox

            entry = bib_data[values["-ENTRY LIST-"][0].key]
            ID = choose_entry(window, entry)
        elif event == "Copy":
            if not ID == "":
                pyperclip.copy(ID)
        elif event == "Edit":
            if ID == "":
                sg.popup("No entry selected")
                continue
            edited_entry_text = popup_get_Mtext( "Please edit the bibtex code for the entry to be added below"
                                               , default_text=parsebibtex.entry_repr(bib_data[ID])
                                               , title="Edit"
                                               , size=(50,10)
                                               )
            f = io.StringIO(edited_entry_text)
            new_lib = parsebibtex.parse_library(f)
            if not len(new_lib) == 1:
                sg.popup("Edit is not the place to insert new entries.")
                continue
            for cite_key in new_lib:
                edited_entry = new_lib[cite_key]

            if not ID == edited_entry["cite_key"]:
                bib_data.pop(ID)
            bib_data[edited_entry["cite_key"]] = edited_entry
            search_for_occurance(window, values["-SEARCH-"], bib_data)
            ID = choose_entry(window, edited_entry)

        elif event == "-SEARCH-":
            search_for_occurance(window, values["-SEARCH-"], bib_data)

    window.close()

