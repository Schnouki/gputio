#!/usr/bin/env python2

import putio

import pygtk
pygtk.require('2.0')
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
        self.tree = gtk.TreeStore(str, int)

        # Scrolled window (for the tree view)
        sw = gtk.ScrolledWindow()
        hbox.pack_start(sw)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        # Tree view
        treeview = gtk.TreeView(self.tree)
        sw.add(treeview)
        treeview.set_enable_tree_lines(True)
        treeview.set_search_column(0)
        treeview.set_rules_hint(True)

        # Add columns
        cell = gtk.CellRendererText()
        tvc = gtk.TreeViewColumn("Name", cell, text=0)
        treeview.append_column(tvc)
        tvc.set_expand(True)
        tvc.set_sort_column_id(0)

        cell = gtk.CellRendererText()
        cell.set_property("xalign", 1.0)
        tvc = gtk.TreeViewColumn("Size", cell)
        tvc.set_cell_data_func(cell, self._render_size)
        treeview.append_column(tvc)
        tvc.set_sort_column_id(1)

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
        self._get_folder(0, None)

    def _get_folder(self, root, parent):
        items = self.api.get_items(parent_id=root)
        for it in items:
            tree_iter = self.tree.append(parent, (it.name, int(it.size)))
            if it.is_dir:
                self._get_folder(it.id, tree_iter)

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
