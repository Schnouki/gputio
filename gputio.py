#!/usr/bin/env python2

import mimetypes
import putio

import pygtk
pygtk.require('2.0')
import gio
import glib
import gtk

class GPutIO(object):
    def __init__(self, apikey, apisecret):
        # Main window
        win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        win.set_title("GPutIO")
        win.connect("destroy", self.destroy)
        hbox = gtk.HBox()
        win.add(hbox)

        # Tree store
        self.tree = gtk.TreeStore(str, int, gtk.gdk.Pixbuf)

        # Scrolled window (for the tree view)
        sw = gtk.ScrolledWindow()
        hbox.pack_start(sw)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        # Tree view
        self.tv = gtk.TreeView(self.tree)
        sw.add(self.tv)
        self.tv.set_enable_tree_lines(True)
        self.tv.set_search_column(0)
        self.tv.set_rules_hint(True)

        # Cell renderers
        cell_txt = gtk.CellRendererText()
        cell_txt_right = gtk.CellRendererText()
        cell_txt_right.set_property("xalign", 1.0)
        cell_pb = gtk.CellRendererPixbuf()

        # Add columns
        tvc = gtk.TreeViewColumn("Name")
        tvc.pack_start(cell_pb, expand=False)
        tvc.pack_start(cell_txt)
        tvc.add_attribute(cell_txt, "text", 0)
        tvc.add_attribute(cell_pb, "pixbuf", 2)
        tvc.set_expand(True)
        tvc.set_sort_column_id(0)
        self.tv.append_column(tvc)

        tvc = gtk.TreeViewColumn("Size", cell_txt_right)
        tvc.set_cell_data_func(cell_txt_right, self._render_size)
        tvc.set_sort_column_id(1)
        self.tv.append_column(tvc)

        # Buttons box
        bbox = gtk.VButtonBox()
        hbox.pack_start(bbox, expand=False)
        bbox.set_layout(gtk.BUTTONBOX_START)
        
        btn = gtk.Button(stock = gtk.STOCK_REFRESH)
        btn.connect("clicked", self.refresh)
        bbox.pack_start(btn)

        btn = gtk.Button(stock = gtk.STOCK_SAVE)
        bbox.pack_start(btn)

        btn = gtk.Button(stock = gtk.STOCK_DELETE)
        bbox.pack_start(btn)

        btn = gtk.Button(stock = gtk.STOCK_QUIT)
        btn.connect("clicked", self.destroy)
        bbox.pack_start(btn)
        bbox.set_child_secondary(btn, True)

        # API init
        self.api = putio.Api(apikey, apisecret)

        win.show_all()

        self.refresh()

    def refresh(self, data=None):
        self.tree.clear()
        glib.idle_add(self._get_folder, 0, None, priority=glib.PRIORITY_LOW)

    def _get_folder(self, root, parent):
        items = self.api.get_items(parent_id=root)
        theme = gtk.icon_theme_get_default()
        for it in items:
            if it.is_dir:
                pb = theme.load_icon("folder", 16, 0)
                tree_iter = self.tree.append(parent,
                                             (it.name, int(it.size), pb))
                glib.idle_add(self._get_folder, it.id, tree_iter,
                              priority=glib.PRIORITY_LOW)

            else:
                pb = None
                (file_type, encoding) = mimetypes.guess_type(it.name)
                if file_type is not None:
                    icon_names = gio.content_type_get_icon(file_type).get_names()
                    pb = theme.choose_icon(icon_names, 16, 0).load_icon()
                tree_iter = self.tree.append(parent,
                                             (it.name, int(it.size), pb))

            self.tv.queue_draw()
            self.tv.window.process_updates(True)

    # Render the size in a CellRenderer
    def _render_size(self, col, cell, model, iter, data=None):
        size = model.get_value(iter, 1)
        if size <= 0:
            size = ""
        elif size < 1024:
            size = "%d B" % size
        elif size < 1024**2:
            size = "%.1f kB" % (size/1024.)
        elif size < 1024**3:
            size = "%.1f MB" % (size/(1024.**2))
        else:
            size = "%.1f GB" % (size/(1024.**3))
        cell.set_property("text", size)

    def destroy(self, widget, data=None):
        gtk.main_quit()


def queue_download(path, url):
    # d4x -d "path" "url"
    pass

if __name__ == "__main__":
    # Read config file
    with open("config") as f:
        apikey = f.readline().strip()
        apisecret = f.readline().strip()
    gputio = GPutIO(apikey, apisecret)
    gtk.main()
