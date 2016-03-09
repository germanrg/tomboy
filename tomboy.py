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

def get_start_here(tomboy):
	return tomboy.FindStartHereNote()
def get_note_by_title(tomboy, title):
	return tomboy.FindNote(title)
def get_note_by_notebook(tomboy, notebook):
	pass
def invalid():
   print "INVALID CHOICE!"
search_menu = {"1":("Get 'Start Here' note", get_start_here), 
				"2":("Get note by title", get_note_by_title),
				"3":("Get note by notebook", get_note_by_notebook)
       		}

# This class model a complete XML Tomboy note. Used to create new notes. 
class XmlNote():
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
# This function prints the script banner
def print_header():
	os.system("clear")
	print header
# This function prints a given Tomboy note details on stdout
def display_note(tomboy, note):
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
# This function checks if Tomboy is running
def isRunning():
	for i in psutil.process_iter():
		if i.name() == "tomboy":
			return i.pid
	return 0
# This function gets all Tomboy notebooks 
def get_notebooks(tomboy, notebook_names, notebook_uris):
	for x in tomboy.ListAllNotes():
		tags = tomboy.GetTagsForNote(x)
		for t in tags:
			if t[:16] == 'system:notebook:':
				notebook_names.append(t[16:])
				notebook_uris.append(x)
#This function shows the main menu
def main_menu():
	option = '0'
	print("\t1 - New Note")
	print("\t2 - Search Note")
	print("\t3 - Get Notebooks")
	print("\t4 - Exit")
	option = raw_input("\nSelect option: ")
	if option == '1' or option == '2' or option == '3' or option == '4':
		return option
	else:
		return '0'
#This function shows the search menu
def search_menu():
	option = '0'
	print("\t1 - Find 'Start Here' Note")
	print("\t2 - Search Note by title")
	print("\t3 - Back to main menu")
	option = raw_input("\nSelect option: ")
	if option == '1' or option == '2' or option == '3':
		return option
	else:
		return '0'
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
			print "Invalid option. Try again.\n\n\n"
			note_option = ''
# This function search and kill Tomboy processes.
def close_tomboy(tomboy_pid):
	print "Terminating Tomboy processes..."
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

parser = optparse.OptionParser(description = desc, version = version, usage = usage)

parser.add_option("-n", "--new-note", action="store_true",
                    dest="new_flag", default=False,
                    help="Create a new tomboy note")
parser.add_option("-s", "--search", action="store_true",
                    dest="search_flag", default=False,
                    help="Show accepted passwords")
parser.add_option("-t", "--notebooks", action="store_true",
                    dest="notebooks_flag", default=False,
                    help="Show all tomboy notebook names")
(opts, args) = parser.parse_args()

if not opts.new_flag and not opts.search_flag and not opts.notebooks_flag:
	parser.error("Select at least one of this options: [-nst].\n")
	parser.print_help()
	exit(-1)

print_header()
# Kill Tomboy Processes
close_tomboy(isRunning())

# Access the Tomboy remote control interface
print "\nStarting new Tomboy instance... "
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
	search_option = '0'
	while search_option != '-1':
		search_option = search_menu()
		# Search 'Start Here' Note
		if search_option == '1':
			print_header()
			sh = tomboy.FindStartHereNote()
			if not sh: print "'Start Here' Note not found!\n"
			else: 
				print "\nStart Here note: " + str(sh) + '\n'
				note_options(tomboy, sh)
				search_option = '-1'
		# Search note by title
		elif search_option == '2':
			print_header()
			search_title = raw_input("\nEnter the Title to search: ")
			n = tomboy.FindNote(search_title)
			if not n: print "\nNote not found!\n"
			else: 
				print "\nSearch note: " + str(n) + '\n'
				note_options(tomboy, n)
				search_option = '-1'
		elif search_option == '3': search_option = '-1'
		else: print "\nIncorrect option. Try again.\n"

if opts.notebooks_flag:
	print_header()
	notebook_uris = []
	notebook_names = []
	get_notebooks(tomboy, notebook_names, notebook_uris)
	# Remove duplicates
	aux = set(notebook_names)
	notebook_names = list(aux)
	aux = set(notebook_uris)
	notebook_uris = list(aux)

	out = "NoteBooks: "
	for x in notebook_names:
		out += x + ', '
	print out[:-2] + "\n"

# Kill Tomboy processes
close_tomboy(isRunning())

'''
def get_start_here(tomboy):
	return tomboy.FindStartHereNote()

def get_note_by_title(tomboy, title):
	return tomboy.FindNote(title)

def get_note_by_notebook(tomboy, notebook):
	pass

def invalid():
   print "INVALID CHOICE!"

notes_menu = {"1":("Display note in tomboy", note_display_tomboy),
        "2":("Display note below", note_display_text),
        "3":("Edit note", note_edit),
        "4":("Delete note", note_delete)
       }
for key in sorted(searc_menu.keys()):
     print key+":" + search_menu[key][0]

ans = raw_input("Make A Choice")
search_menu.get(ans,[None,invalid])[1]()
'''