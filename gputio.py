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
        self.tree = gtk.TreeStore(str, str)
        
        # Tree view
        self.treeview = gtk.TreeView()
        hbox.pack_start(self.treeview)
        self.treeview.set_enable_tree_lines(True)

        # Cell renderer
        cell = gtk.CellRendererText()

        # Add columns
        tvc = gtk.TreeViewColumn("Name", cell, text=0)
        self.treeview.append_column(tvc)
        tvc.set_expand(True)

        tvc = gtk.TreeViewColumn("Size", cell, text=1)
        self.treeview.append_column(tvc)

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

    def refresh(self, data=None):
        self.tree.clear()
        self._get_folder(0, None)
        self.treeview.set_model(self.tree)

    def _get_folder(self, root, parent):
        items = self.api.get_items(parent_id=root)
        for it in items:
            tree_iter = self.tree.append(parent, (it.name, self._render_size(it.size)))
            if it.is_dir:
                self._get_folder(it.id, tree_iter)

    def _render_size(self, size):
        size = int(size)
        if size <= 0:
            return ""
        elif size < 1024:
            return "%d B" % size
        elif size < 1024**2:
            return "%.1f kB" % (size/1024.)
        elif size < 1024**3:
            return "%.1f MB" % (size/(1024.**2))
        else:
            return "%.1f GB" % (size/(1024.**3))

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
