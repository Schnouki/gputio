from distutils.core import setup

from distutils import cmd
from distutils.command.build import build as _build
from distutils.command.install_data import install_data as _install_data
import distutils.dist
from distutils.log import info

import glob
import os
import os.path
import subprocess

class build(_build):
    def run(self):
        _build.run(self)
        self.run_command("build_mo")

class build_mo(cmd.Command):
    description = "build .mo message catalogues"
    
    user_options = [("build-base=", "b", "base directory for build library")]
    def initialize_options(self):
        self.build_base = None
    def finalize_options(self):
        if self.build_base is None:
            self.build_base = "build"

    def _mo_newer(self, po, mo):
        if not os.path.isfile(mo):
            return False
        else:
            return os.path.getmtime(mo) > os.path.getmtime(po)

    def run(self):
        for po_file in glob.glob(os.path.join("po", "*.po")):
            lang = po_file[-5:-3]
            mo_dir = os.path.join(self.build_base, "locale", lang, "LC_MESSAGES")
            mo_file = os.path.join(mo_dir, "gputio.mo")
            if not os.path.isdir(mo_dir):
                info("creating %s" % mo_dir)
                os.makedirs(mo_dir)
            if not self._mo_newer(po_file, mo_file):
                info("compiling '%s'" % mo_file)
                subprocess.check_call(["msgfmt", "-o", mo_file, po_file])

class install_data(_install_data):
    def finalize_options(self):
        _install_data.finalize_options(self)
        locale_dir = os.path.join("share", "locale")
        patt = os.path.join("build", "locale", "*", "LC_MESSAGES", "gputio.mo")
        for mo in glob.glob(patt):
            lang = os.path.basename(os.path.dirname(os.path.dirname(mo)))
            dest_dir = os.path.join("share", "locale", lang, "LC_MESSAGES")
            self.data_files.append((dest_dir, [mo]))

setup(name="gputio",
      version="0.1",
      description="A desktop client for Put.io",
      author="Thomas Jost",
      author_email="schnouki@schnouki.net",
      url="https://github.com/Schnouki/gputio",
      requires=["pygtk", "putio"],
      scripts=["gputio"],

      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: X11 Applications :: GTK",
                   "Intended Audience :: End Users/Desktop",
                   "License :: OSI Approved :: ISC License (ISCL)",
                   "Topic :: Communications :: File Sharing",
                   "Topic :: Internet :: WWW/HTTP",
                   ],
      data_files = [(os.path.join("share", "gputio"), ["gputio.conf.sample"])],
      cmdclass={
          "build": build,
          "build_mo": build_mo,
          "install_data": install_data,
          },
      )
