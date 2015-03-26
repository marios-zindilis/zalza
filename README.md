Zalza
=====

**Zalza** is the Python script with which I maintain my website, 
[zindilis.com](http://zindilis.com/).

It traverses a directory with the sources of the website (mostly written in 
Markdown), and produces HTML files. This script is triggered by a post-merge 
Git hook, inside the local repository of the Markdown sources, on the web 
server. A `git pull` is executed periodically on the web server, and Git only 
executes the hook if there are updates.

