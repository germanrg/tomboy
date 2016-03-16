#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# A simple python script to get and set Tomboy notes  
# from terminal.
#
# The script uses an extra lib: psutil
# To install it try: easy_install psutil
# * Maybe you have to install python-dev if you get an error 
#   during the installation of psutil.
#
# gNrg(at)tuta.io
#

import dbus, gobject, dbus.glib
import psutil  # sudo apt-get install python-dev; sudo easy_install psutil
import time
import os
import optparse
from datetime import datetime

header = """
    +-------------------------------------------------+
    |                                                 |
    |                    Tomboy.py                    |
    |                     by gNrg                     |
    |                                                 |
    +-------------------------------------------------+\n
"""
version = "%prog V0.1"
usage = "usage: %prog [-h] [-nst]"
desc = """Simply script to manage tomboy from terminal. You can 
create new tomboy notes, search notes by title or tag
to display or edit them and get all tomboy notebooks.
For more information about script usage and options
use -h. """

def print_header():
    '''Clear screen and prints banner'''
    os.system("clear")
    print header
def isRunning():
    '''Checks if Tomboy is running'''
    for i in psutil.process_iter():
        if i.name() == "tomboy":
            return i.pid
    return 0
def get_notebooks(tomboy, notebook_names):
    '''Get all Tomboy notebooks'''
    for x in tomboy.ListAllNotes():
        tags = tomboy.GetTagsForNote(x)
        for t in tags:
            if t[:16] == 'system:notebook:':
                notebook_names.append(t[16:])
def get_start_here(tomboy):
    return [tomboy.FindStartHereNote()]
def get_note_by_title(tomboy):
    title = raw_input("\n\tTitle: ")
    return [tomboy.FindNote(title)]
def get_note_by_notebook(tomboy):
    notebook = raw_input("\n\tNotebook: ")
    notebooks = []
    get_notebooks(tomboy, notebooks)
    if notebook in notebooks: "\n\t[[ OK ]] Notebook exist: " + notebook + "\n"
    else: print "\n\t[[ ERROR ]] Notebook not found\n"
def save_text_note(tomboy, note):
    print 'Save text note'
def save_xml_note(tomboy, note):
    print 'Save XML note'
def edit_note(tomboy, note):
    print 'Edit note'
def display_note(tomboy, note):
    '''Prints a given Tomboy note details on stdout'''
    print "\n\tTitle:\t" + str(tomboy.GetNoteTitle(note))
    print "\tCreate date:\t" + str(tomboy.GetNoteCreateDate(note)) # Improve format!
    print "\tChange date:\t" + str(tomboy.GetNoteChangeDate(note)) # Improve format!
    print "\tContents:\t" 
    print tomboy.GetNoteContents(note)
    tags = tomboy.GetTagsForNote(note)
    if tags:
        print "\tTags:\t\t"
        for t in tags:
            print '\t\t - ' + str(t)
    else:
        print "\tTags:\t\tNone"
    print ""
def invalid_option():
    print "\n\t[[ ERROR ]] Incorrect option\n"
def close_tomboy(tomboy_pid):
    '''Search and kill Tomboy processes'''
    print "\tTerminating Tomboy processes..."
    tomboy_flag = False
    if tomboy_pid:
        for i in psutil.process_iter():
            if i.name() == "tomboy":
                p = i.pid
                i.terminate()
                print "\n\t[[ OK ]] - Tomboy process terminated succesfully. PID: " + str(p)
                tomboy_flag = True
    if not tomboy_flag: print "\n\t[[ OK ]] - There isn't tomboy processes running."
    time.sleep(2)

search_menu = {"1":("Get 'Start Here' note", get_start_here), 
                "2":("Get note by title", get_note_by_title),
                "3":("Get note by notebook", get_note_by_notebook)
            }
notes_menu = {"1":("Display note below", display_note), 
                "2":("Save note in plain text", save_text_note),
                "3":("Save note in XML ", save_xml_note),
                "4":("Edit note", edit_note)
            }

class XmlNote():
    '''Complete XML Tomboy Note'''
    def __init__(self):
        self.xml_base = ''
        self.xml_headers = '<?xml version="1.0" encoding="utf-8"?>' + '\n'
        self.xml_headers += '<note version="0.3" xmlns:link="http://beatniksoftware.com/tomboy/link" xmlns:size="http://beatniksoftware.com/tomboy/size" xmlns="http://beatniksoftware.com/tomboy">' + '\n'
        self.xml_title = '<title></title>' + '\n'
        self.xml_content = '<text xml:space="preserve"><note-content version="0.1"></note-content></text>' + '\n'
        self.xml_last_change_date = '<last-change-date></last-change-date>' + '\n'
        self.xml_meta_change_date = '<last-metadata-change-date></last-metadata-change-date>' + '\n'
        self.xml_create_date = '<create-date></create-date>' + '\n'
        self.xml_cursor_pos = '<cursor-position>0</cursor-position>' + '\n'
        self.xml_bound_pos = '<selection-bound-position>-1</selection-bound-position>' + '\n'
        self.xml_width = '<width>450</width>' + '\n'
        self.xml_height = '<height>360</height>' + '\n'
        self.xml_x = '<x>0</x>' + '\n'
        self.xml_y = '<y>0</y>' + '\n'
        self.xml_tags = '<tags>' + '\n\n' + '</tags>' + '\n'
        self.xml_on_startup = '<open-on-startup></open-on-startup>' + '\n' + '</note>' # True or False
    def __mount_xml__(self):
        self.xml_base += self.xml_headers + self.xml_title + self.xml_content
        self.xml_base += self.xml_last_change_date + self.xml_meta_change_date + self.xml_create_date
        self.xml_base += self.xml_cursor_pos + self.xml_bound_pos + self.xml_width + self.xml_height + self.xml_x + self.xml_y
        self.xml_base += self.xml_tags + self.xml_on_startup
    def set_title(self, title):
        new_title = self.xml_title[:7] + title + self.xml_title[7:]
        self.xml_title = new_title
        new_content = self.xml_content[:-23] + title + '\n\n' + self.xml_content[-23:]
        self.xml_content = new_content
    def set_content(self, content):
        new_content = self.xml_content[:-23] + content + self.xml_content[-23:]
        self.xml_content = new_content
    def set_notebook(self, tag):
        new_tag = self.xml_tags[:-10] + '<tag>system:notebook:' + tag + '</tag>' + self.xml_tags[-10:]
        self.xml_tags = new_tag
    def set_startup(self, startup): # Bool
        new_startup = self.xml_on_startup[:-26]
        if startup: new_startup += 'True'
        else: new_startup += 'False'
        new_startup += self.xml_on_startup[-26:]
        self.xml_on_startup = new_startup
    def set_date(self, formatted_date):
        new_lcd = self.xml_last_change_date[:-20]
        new_lcd += formatted_date + self.xml_last_change_date[-20:]
        self.xml_last_change_date = new_lcd

        new_mcd = self.xml_meta_change_date[:-29]
        new_mcd += formatted_date + self.xml_meta_change_date[-29:]
        self.xml_meta_change_date = new_mcd

        new_cd = self.xml_create_date[:-15]
        new_cd += formatted_date + self.xml_create_date[-15:]
        self.xml_create_date = new_cd
    def create_note(self, tomboy):
        dt = datetime.now() 
        formatted_date = dt.strftime('%Y-%m-%dT%H:%M:%S.0000000')
        formatted_date += '+1:00'
        self.set_date(formatted_date)
        self.__mount_xml__()
        new_note = tomboy.CreateNote()
        tomboy.SetNoteCompleteXml(new_note, self.xml_base)
        self.xml_base = ''

# This function shows note options menu
def note_options(tomboy, note):
    note_option = ''
    while note_option == '':
        print "Note options:\n"
        print "1 - Edit note in tomboy"
        print "2 - Display note below"
        note_option = raw_input("\nSelect option: ")
        if note_option == '1': 
            tomboy.DisplayNote(note)
            time.sleep(3)
            raw_input("\nPress any key to continue... ")
        elif note_option == '2':
            display_note(tomboy, note)
            raw_input("\nPress any key to continue... ")
        else:
            print "[[ ERROR ]] Invalid option. Try again.\n\n\n"
            note_option = ''

parser = optparse.OptionParser(description = desc, version = version, usage = usage)
parser.add_option("-n", "--new-note", action="store_true",
                    dest="new_flag", default=False,
                    help="Create a new tomboy note")
parser.add_option("-s", "--search", action="store_true",
                    dest="search_flag", default=False,
                    help="Search notes by title or notebook")
parser.add_option("-t", "--notebooks", action="store_true",
                    dest="notebooks_flag", default=False,
                    help="Show all tomboy notebook names")
(opts, args) = parser.parse_args()

if not opts.new_flag and not opts.search_flag and not opts.notebooks_flag:
    parser.error("Select at least one of this options: [-nst].\n")
    parser.print_help()
    exit(-1)

print_header()
close_tomboy(isRunning())

# Access the Tomboy remote control interface
print "\n\tStarting new Tomboy instance... "
try:
    bus = dbus.SessionBus()
    obj = bus.get_object("org.gnome.Tomboy","/org/gnome/Tomboy/RemoteControl")
    tomboy = dbus.Interface(obj, "org.gnome.Tomboy.RemoteControl")
    print "\n\t[[ OK ]] - Tomboy started."
    # Give a little to run it.
    time.sleep(2)
except:
    print "\n\t[[ ERROR ]] - Can't get Tomboy object from DBUS."
    exit(1)

# Creating new note
if opts.new_flag:
    print_header()
    print "Note details: \n"
    new_note = XmlNote()
    time.sleep(2)
    title = raw_input("\tTitle: ")
    content = raw_input("\tContent [Press enter to finish]: ")
    startup = raw_input("\tShow note on startup?[y/N]: ")
    if startup == 'Y' or startup == 'y': startup = True
    else: startup = False
    notebook = raw_input("\tNotebook[Not required]: ")

    if len(notebook) > 1: new_note.set_notebook(notebook)
    new_note.set_title(title) 
    new_note.set_content(content)
    new_note.set_startup(startup)
    new_note.create_note(tomboy)
    time.sleep(2)
    print '\n\t[[ OK ]] - Note created succesfully!\n'

if opts.search_flag:
    print_header()
    for key in sorted(search_menu.keys()):
        print "\t" + key + " - " + search_menu[key][0]
    o = raw_input("\n\tSelect option: ")
    ans = search_menu.get(o,[None,invalid_option])[1](tomboy)
    if o == '1' or o == '2':
        if not ans[0]: print "\n\t[[ ERROR ]] - Note not found!\n"
        else:
            print_header()
            print "\n\t[[ OK ]] - Note: " + str(ans[0]) + '\n'
            for key in sorted(notes_menu.keys()):
                print "\t" + key + " - " + notes_menu[key][0]
            o = raw_input("\n\tSelect option: ")
            note_o = notes_menu.get(o,[None,invalid_option])[1](tomboy, ans[0])
    elif o == '3':
        if not ans[0]: print "\n\t[[ ERROR ]] - Notebook empty or not found!\n"

if opts.notebooks_flag:
    print_header()
    notebook_names = []
    get_notebooks(tomboy, notebook_names)
    notebook_names = set(list(notebook_names)) # Remove duplicates
    if not len(notebook_names): out = "\tThere isn't notebooks.\n"
    else: out = "NoteBooks: "
    for x in notebook_names:
        out += x + ', '
    print out[:-2] + "\n"

# Kill Tomboy processes
close_tomboy(isRunning())