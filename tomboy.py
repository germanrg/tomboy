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

# Kill Tomboy Processes
print "Terminating existent tomboy processes... "
tomboy_pid = isRunning()
if tomboy_pid != 0:
	for i in psutil.process_iter():
		if i.name() == "tomboy":
			p = i.pid
			i.terminate()
			print "[[ OK ]] - Tomboy process terminated succesfully. PID: " + str(p)
	time.sleep(2)

# Access the Tomboy remote control interface
print "Starting new Tomboy instance... "
try:
	bus = dbus.SessionBus()
	obj = bus.get_object("org.gnome.Tomboy","/org/gnome/Tomboy/RemoteControl")
	tomboy = dbus.Interface(obj, "org.gnome.Tomboy.RemoteControl")
	print "[[ OK ]] - Tomboy started."
	# Give a little to run it.
	time.sleep(2)
except:
	print "[[ ERROR ]] - Can't get Tomboy object from DBUS."
	exit(1)

# Process menu option
option = main_menu()
while option != '':
	if option == '1':
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
		print 'Not implemented'
		option = main_menu()

	elif option == '3':
		# Get notebooks
		notebook_uris = []
		notebook_names = []
		get_notebooks(tomboy, notebook_names, notebook_uris)
		print("NoteBooks: ")
		for x in notebook_names:
			print "\t - " + x
		print "\n\n\n"
		option = main_menu()

	elif option == '4':
		option = ''

	else:
		print "Incorrect option. Try again!"
		option = main_menu()

# Close tomboy running instances
tomboy_pid = isRunning()
if tomboy_pid == 0:
	print "Tomboy is not running."
else:
	print "Terminating tomboy process... "
	for i in psutil.process_iter():
		if i.name() == "tomboy":
			i.terminate()
	time.sleep(2)

### http://arstechnica.com/information-technology/2007/09/using-the-tomboy-d-bus-interface/
### https://github.com/ducdebreme/tomboy-scripts
### http://workhorsy.org/junk/tomboy_notify_py.txt