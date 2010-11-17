from distutils.core import setup

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
      )
