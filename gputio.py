#!/usr/bin/env python2

import mimetypes
import threading
import webbrowser

import putio

import pygtk
pygtk.require('2.0')
import gio
import gobject
import gtk

class GPutIO(object):
    def __init__(self, apikey, apisecret):
        # Main window
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_title("GPutIO")
        self.win.connect("destroy", self.destroy)
        hbox = gtk.HBox()
        self.win.add(hbox)
        vpaned = gtk.VPaned()
        hbox.pack_start(vpaned)

        # Data stores
        # - TreeStore for the files tree: name, size, icon, ID, URL
        self.tree = gtk.TreeStore(str, int, gtk.gdk.Pixbuf, int, str)
        # - ListStore for the downloads: name, URL, total size, downloaded size
        self.list = gtk.ListStore(str, str, int, int)

        # Scrolled window for the files tree
        swf = gtk.ScrolledWindow()
        vpaned.pack1(swf, resize=True)
        swf.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # Scrolled window for the downloads list
        swd = gtk.ScrolledWindow()
        vpaned.pack2(swd, resize=False)
        swd.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        # TreeView for the files tree
        self.tvf = gtk.TreeView(self.tree)
        swf.add(self.tvf)
        self.tvf.set_enable_tree_lines(True)
        self.tvf.set_search_column(0)
        self.tvf.set_rules_hint(True)
        self.tvf.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        # TreeView for the downloads list
        self.tvd = gtk.TreeView(self.list)
        swd.add(self.tvd)
        self.tvd.set_search_column(0)
        self.tvd.set_rules_hint(True)

        # Cell renderers
        cell_txt = gtk.CellRendererText()
        cell_txt_right = gtk.CellRendererText()
        cell_txt_right.set_property("xalign", 1.0)
        cell_pb = gtk.CellRendererPixbuf()
        cell_prog = gtk.CellRendererProgress()

        # Add columns
        tvc = gtk.TreeViewColumn("Name")
        tvc.pack_start(cell_pb, expand=False)
        tvc.pack_start(cell_txt)
        tvc.add_attribute(cell_txt, "text", 0)
        tvc.add_attribute(cell_pb, "pixbuf", 2)
        tvc.set_expand(True)
        tvc.set_sort_column_id(0)
        self.tvf.append_column(tvc)

        tvc = gtk.TreeViewColumn("Size", cell_txt_right)
        tvc.set_cell_data_func(cell_txt_right, self._render_size)
        tvc.set_sort_column_id(1)
        self.tvf.append_column(tvc)

        tvc = gtk.TreeViewColumn("File name", cell_txt, text=0)
        tvc.set_sort_column_id(0)
        tvc.set_expand(True)
        tvc.set_resizable(True)
        self.tvd.append_column(tvc)

        tvc = gtk.TreeViewColumn("Progress", cell_prog)
        tvc.set_cell_data_func(cell_prog, self._render_progress)
        tvc.set_sort_column_id(3)
        self.tvd.append_column(tvc)

        self.tvd.set_tooltip_column(1)

        # Default sorting order
        self.tree.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.list.set_sort_column_id(0, gtk.SORT_ASCENDING)

        # Buttons box
        bbox = gtk.VButtonBox()
        hbox.pack_start(bbox, expand=False)
        bbox.set_layout(gtk.BUTTONBOX_START)
        
        btn = gtk.Button(stock = gtk.STOCK_REFRESH)
        btn.connect("clicked", self.refresh)
        bbox.pack_start(btn)

        btn = gtk.Button(stock = gtk.STOCK_SAVE)
        btn.connect("clicked", self.download)
        bbox.pack_start(btn)

        btn = gtk.Button(stock = gtk.STOCK_DELETE)
        btn.connect("clicked", self.remove)
        bbox.pack_start(btn)

        btn = gtk.Button(stock = gtk.STOCK_QUIT)
        btn.connect("clicked", self.destroy)
        bbox.pack_start(btn)
        bbox.set_child_secondary(btn, True)

        # API init
        self.api = putio.Api(apikey, apisecret)

        # Icons
        self.theme = gtk.icon_theme_get_default()
        self.icons = {}

        self.win.show_all()

        self.refresh()

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

    # Render the progress of a download in a CellRenderer
    def _render_progress(self, col, cell, model, iter, data=None):
        total, downloaded = model.get(iter, 2, 3)
        cell.set_property("value", 100.*downloaded/total)

    # Refresh the TreeView using the Put.io API
    def refresh(self, data=None):
        t = threading.Thread(target=self._get_folder, args=(0, None))
        self.tree.clear()
        t.start()

    # Fetch data from a Put.io folder and add it in the TreeStore
    def _get_folder(self, root, parent):
        items = self.api.get_items(parent_id=root)
        dirs = []
        for it in items:
            pb = None
            if it.is_dir:
                pb = self._get_icon(("folder",))
            else:
                (file_type, encoding) = mimetypes.guess_type(it.name)
                icon_names = ("misc",)
                if file_type is not None:
                    with gtk.gdk.lock:
                        icon_names = gio.content_type_get_icon(file_type).get_names()
                pb = self._get_icon(icon_names)
                
            tree_iter = self.tree.append(parent,
                                         (it.name, int(it.size), pb, int(it.id), it.download_url))
            if it.is_dir:
                dirs.append((it.id, tree_iter))
        
        for (it_id, tree_iter) in dirs:
            self._get_folder(it_id, tree_iter)

    # Get an icon from the default theme, using a cache if possible
    def _get_icon(self, names):
        # Try from cache
        for name in names:
            if name in self.icons:
                return self.icons[name]

        # Not in cache --> try to get it from Gtk and cache it
        with gtk.gdk.lock:
            pb = self.theme.choose_icon(names, 16, 0).load_icon()
        for name in names:
            self.icons[name] = pb
        return pb

    # Download selected items
    def download(self, data=None):
        sel = self.tvf.get_selection()
        model, rows = sel.get_selected_rows()
        for row in rows:
            tree_iter = model.get_iter(row)
            url = model.get_value(tree_iter, 4)
            if len(url) == 0:
                continue
            webbrowser.open(url)

    # Remove selected items
    def remove(self, data=None):
        sel = self.tvf.get_selection()
        model, rows = sel.get_selected_rows()
        if len(rows) == 0:
            return
        
        names = []
        ids = []
        for row in rows:
            tree_iter = model.get_iter(row)
            name, id_ = model.get(tree_iter, 0, 3)
            names.append(name)
            ids.append(id_)

        txt = "The following items will be removed:"
        for name in names:
            txt += "\n- "+name
        txt += "\n\nAre you sure you want to remove them?"

        dlg = gtk.MessageDialog(self.win, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, txt)
        dlg.set_title("Really remove?")
        resp = dlg.run()

        if resp == gtk.RESPONSE_YES:
            for id_ in ids:
                item = self.api.get_items(id=id_)[0]
                item.delete_item()
            self.refresh()
        dlg.destroy()

    # Quit the app
    def destroy(self, widget, data=None):
        gtk.main_quit()

if __name__ == "__main__":
    # Read config file
    with open("config") as f:
        apikey = f.readline().strip()
        apisecret = f.readline().strip()
    gobject.threads_init()
    gputio = GPutIO(apikey, apisecret)
    gtk.main()
