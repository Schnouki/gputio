About GPutio
============

GPutio is a desktop client for [Put.io](http://put.io/), an online storage
service that fetches media files and lets you stream them immediately.

Using this client, you can easily manage your files on Put.io:

- download them locally with curl, a rock-solid downloader
- remove them from your Put.io account
- ...probably more to come :)

GPutio is a free software, available under the terms of the
[ISC license](http://en.wikipedia.org/wiki/ISC_license). It is written in
[Python](http://www.python.org/) and uses the [Gtk](http://www.gtk.org/) toolkit
through its [PyGTK](http://www.pygtk.org/) binding.
[PycURL](http://pycurl.sourceforge.net/) is used for downloading stuff from the
Internet; it uses the awesome [libcurl](http://curl.haxx.se/libcurl/) library.

GPutio has only been tested on Linux so far, but it *should* work on almost any
other platform (as long as Python, Gtk and PycURL are available). It has been
developed and tested with Python 2.7, but it should work with Python 2.6 too.

How to use
==========

1. Install Python, GTK, PyGTK and PycURL. On Linux, you will probably want to use
   your favorite package manager (`apt-get` for Debian/Ubuntu, `pacman` for Arch
   Linux, `yum` for Fedora, `tar` for Slackware...)

2. Get a copy of GPutio: use the big "Download" button, or run the following
   command: `git clone git://github.com/Schnouki/gputio.git`

3. Go to the directory you just created and create a configuration file: `cd
   gputio; $EDITOR config`, then fill it with the following content:
   
        [account]
        username = PUTIO_USERNAME
        password = PUTIO_PASSWORD
        
        [api]
        key = PUTIO_API_KEY
        secret = PUTIO_API_SECRET

4. Download the Python version of the
   [Put.io library](http://putio-api.googlecode.com/svn/trunk/putio.py)` (Arch
   Linux users: this is also available
   [in the AUR](http://aur.archlinux.org/packages.php?ID=43611).)

5. Run it: `./gputio.py`

Have fun! :)
