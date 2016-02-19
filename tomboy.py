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
from datetime import datetime

tomboy_path = "/home/gnrg/.local/share/tomboy/"

class XmlNote():
	def __init__(self):
		self.xml_base = ''
		self.xml_headers = '<?xml version="1.0" encoding="utf-8"?>' + '\n'
		self.xml_headers += '<note version="0.3" xmlns:link="" xmlns:size="" xmlns="">' + '\n'
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
		
		file = open(tomboy_path + self.xml_title[7:-9] + formatted_date + '.note','w+')
		file.write(self.xml_base)
		file.close()
		self.xml_base = ''

def print_header():
	os.system("clear")
	print "+---------------------------------------------+"
	print "|                                             |"
	print "|                  Tomboy.py                  |"
	print "|                   by gNrg                   |"
	print "|                                             |"
	print "+---------------------------------------------+"
	print ""

# Check if Tomboy is running
def isRunning():
	for i in psutil.process_iter():
		if i.name() == "tomboy":
			return i.pid
	return 0

def get_notebooks(tomboy, notebook_names, notebook_uris):
	for x in tomboy.ListAllNotes():
		title = tomboy.GetNoteTitle(x)
		if title[:34] == "Plantilla del cuaderno de notas de":
			notebook_names.append(title[35:])
			notebook_uris.append(x)

def main_menu():
	option = '0'
	print("\t1 - New Note")
	print("\t2 - Search Note/s")
	print("\t3 - Get Notebooks")
	print("\t4 - Exit")
	option = raw_input("\nSelect option: ")
	if option == '1' or option == '2' or option == '3' or option == '4':
		return option
	else:
		return '0'

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

# Kill Tomboy Processes
print_header()
print "Terminating existent tomboy processes..."
tomboy_pid = isRunning()
tomboy_flag = False
if tomboy_pid != 0:
	for i in psutil.process_iter():
		if i.name() == "tomboy":
			p = i.pid
			i.terminate()
			print "\n\t[[ OK ]] - Tomboy process terminated succesfully. PID: " + str(p)
			tomboy_flag = True
if not tomboy_flag: print "\n\t[[ OK ]] - There isn't tomboy processes running."
time.sleep(2)
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

# Process menu option
os.system("clear")
print_header()
option = main_menu()
while option != '':
	if option == '1':
		os.system("clear")
		print_header()
		print "Creating new note... "
		new_note = XmlNote()
		time.sleep(2)
		title = raw_input("Title: ")
		content = raw_input("Content [XML/HTML is allowed]: ")
		startup = raw_input("Show note on startup?[y/N]: ")
		if startup == 'Y' or startup == 'y': startup = True
		else: startup = False
		notebook = raw_input("Notebook[Not required]: ")

		if len(notebook) > 1: new_note.set_notebook(notebook)
		new_note.set_title(title) 
		new_note.set_content(content)
		new_note.set_startup(startup)
		new_note.create_note(tomboy)
		time.sleep(2)
		print 'Note created succesfully!\n'
		option = main_menu()

	elif option == '2':
		os.system("clear")
		print_header()
		search_option = '0'
		while search_option != '':
			search_option = search_menu()
			if search_option == '1':
				os.system("clear")
				print_header()
				# Search start here note
				sh = tomboy.FindStartHereNote()
				if not sh: print "'Start Here' Note not found!\n"
				else: print "Start Here note: " + str(sh) + '\n'
			elif search_option == '2':
				os.system("clear")
				print_header()
				search_title = raw_input("\nEnter the Title to search: ")
				n = tomboy.FindNote(search_title)
				if not n: 
					print "\nNote not found!\n"
				else: print "\nSearch note: " + str(n) + '\n'
			elif search_option == '3':
				search_option = ''

		os.system("clear")
		print_header()
		option = main_menu()

	elif option == '3':
		os.system("clear")
		print_header()
		# Get notebooks
		notebook_uris = []
		notebook_names = []
		get_notebooks(tomboy, notebook_names, notebook_uris)
		out = "NoteBooks: "
		for x in notebook_names:
			out += x + ', '
		print out[:-2] + "\n"
		option = main_menu()

	elif option == '4':
		option = '' # Break the loop for close tomboy instance and exit

	else:
		os.system("clear")
		print_header()
		print "\n\t[[ ERROR ]] - Incorrect option. Try again!"
		option = main_menu()

# Close tomboy running instances
print "Terminating tomboy process... "
tomboy_pid = isRunning()
if tomboy_pid == 0:
	print "\n\t[[ OK ]] - There isn't tomboy processes running."
else:
	for i in psutil.process_iter():
		if i.name() == "tomboy":
			p = i.pid
			i.terminate()
			print "\n\t[[ OK ]] - Tomboy process terminated succesfully. PID: " + str(p) + '\n'
	time.sleep(2)

### http://arstechnica.com/information-technology/2007/09/using-the-tomboy-d-bus-interface/
### https://github.com/ducdebreme/tomboy-scripts
### http://workhorsy.org/junk/tomboy_notify_py.txt