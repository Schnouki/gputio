#!/bin/sh

LANGS=fr

xgettext --omit-header --language=Python -o gputio.pot ../gputio || exit 1
for lang in $LANGS; do
    echo -n "$lang: "
    msgmerge -U gputio.$lang.po gputio.pot || exit 1
done
