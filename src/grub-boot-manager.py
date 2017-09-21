#!/usr/bin/env python

from gi.repository import Gtk, Gdk
import subprocess
import re
import os
import sys

# TODO: this stuff need to go to __init__()
f = subprocess.check_output(["grub-install", "--version"])
grub_version = f.split()[-1]

f = open("/boot/grub/grub.cfg", "r").read()
grub_menu_entries = re.findall("menuentry '(.*?)'", f)

f = open("/boot/grub/grubenv", "r").read()
grub_default = re.findall("saved_entry=(.*)", f)[0]

f = open("/etc/default/grub", "r").read()
grub_timeout = re.findall("GRUB_TIMEOUT=(.*)", f)[0]

class GrubBootManager:
    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("grub-boot-manager.ui")

        self.window = builder.get_object("dialog_main")
        self.window.set_title("GRUB Boot Manager")
        self.window.connect("destroy", self.quit)
        #self.window.connect("key-press-event", self._keyhandler)
        self.window.show()

        self.label_version = builder.get_object("label_version")
        self.label_version.set_text(self.label_version.get_text() + grub_version)

        self.treeview = builder.get_object("treeview1")
        self.treeview.connect("row-activated", self.show_dialog_reboot)
        self.liststore = Gtk.ListStore(str)
        self.treeview.set_model(self.liststore)

        self.treeview_column = Gtk.TreeViewColumn("Menu Entry")
        self.treeview.append_column(self.treeview_column)

        self.cellrenderer = Gtk.CellRendererText()
        self.treeview_column.pack_start(self.cellrenderer, True)
        self.treeview_column.add_attribute(self.cellrenderer, "text", 0)

        for entry in grub_menu_entries:
            self.liststore.append([entry])

        self.treeselection = self.treeview.get_selection()
        self.treeselection.connect("changed", self.selection_changed)
        self.treeselection.select_path(grub_menu_entries.index(grub_default))

        self.entry_timeout = builder.get_object("entry_timeout")
        self.entry_timeout.set_text(str(grub_timeout))
        self.entry_timeout.connect("activate", self.grub_set_timeout, grub_timeout)

        self.button_default = builder.get_object("button_default")
        self.button_default.connect("clicked", self.show_dialog_default)

        self.button_reboot = builder.get_object("button_reboot")
        self.button_reboot.connect("clicked", self.show_dialog_reboot)

        self.button_cancel = builder.get_object("button_cancel")
        self.button_cancel.connect("clicked", self.quit)

        # dialog_default
        self.dialog_default = builder.get_object("dialog_default")
        self.dialog_default.set_title("Default - Grub Boot Manager")
        self.dialog_default.connect("delete-event", self.hide_dialog_default)

        self.label_default = builder.get_object("label_default")

        self.button_cancel_default = builder.get_object("button_cancel_default")
        self.button_cancel_default.connect("clicked", self.hide_dialog_default)

        self.button_apply_default = builder.get_object("button_apply_default")
        self.button_apply_default.connect("clicked", self.grub_set_default)

        # dialog_reboot
        self.dialog_reboot = builder.get_object("dialog_reboot")
        self.dialog_reboot.set_title("Reboot - Grub Boot Manager")
        self.dialog_reboot.connect("delete-event", self.hide_dialog_reboot)

        self.label_reboot = builder.get_object("label_reboot")

        self.button_no_reboot = builder.get_object("button_no_reboot")
        self.button_no_reboot.connect("clicked", self.hide_dialog_reboot)

        self.button_yes_reboot = builder.get_object("button_yes_reboot")
        self.button_yes_reboot.connect("clicked", self.grub_reboot)

    '''
    def _keyhandler(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)            
    
        print "Key %s (%d) was pressed" % (keyname, event.keyval)
    
        if Gdk.keyval_name(event.keyval) == 'e':
            self.show_dialog_edit()
    '''

    def selection_changed(self, tree_selection):
        (model, pathlist) = tree_selection.get_selected_rows()
        for path in pathlist:
            tree_iter = model.get_iter(path)
            self.grub_menu_entry = model.get_value(tree_iter, 0)

    def show_dialog_default(self, *args):
        self.label_default.set_text(self.grub_menu_entry)
        self.dialog_default.show()

    def hide_dialog_default(self, *args):
        self.dialog_default.hide()

        return True

    def grub_set_default(self, *args):
        subprocess.Popen(["grub-set-default", self.grub_menu_entry])
        
        self.hide_dialog_default()

    def grub_set_timeout(self, *args):
        grub_timeout = self.entry_timeout.get_text()
        
        if grub_timeout.isdigit():
            subprocess.Popen(["sed", "-i", "-r", "s/GRUB_TIMEOUT=[0-9]+/GRUB_TIMEOUT=%s/" % grub_timeout, "/etc/default/grub"])
            
            subprocess.Popen(["update-grub"])

    def show_dialog_reboot(self, *args):
        self.label_reboot.set_text(self.grub_menu_entry)
        self.dialog_reboot.show()

    def hide_dialog_reboot(self, *args):
        self.dialog_reboot.hide()

        return True

    def grub_reboot(self, *args):
        subprocess.Popen(["grub-reboot", self.grub_menu_entry])
        
        subprocess.Popen(["shutdown", "-r", "now"])

        self.hide_dialog_reboot()

    def show_dialog_edit(self, *args):
        self.dialog_edit.show()

    def hide_dialog_edit(self, *args):
        self.dialog_edit.hide()

        return True

    def quit(self, *args):
        Gtk.main_quit()

if __name__ == "__main__":
    if os.getuid() != 0:
        os.execlp("gksu", "python", sys.argv[0])
    else:
        app = GrubBootManager()
        Gtk.main()
