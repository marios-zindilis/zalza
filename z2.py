#!/usr/bin/python -tt
'''
This script traverses a directory of Markdown files and generates static HTML
pages for my website.
'''
import os
import git

REMOTE = 'https://github.com/marios-zindilis/zindilis.com.git'
LOCAL = '/home/marios/Tests/zindilis.com'
# D_STATE = '/var/zalza/state'
# D_WEB = '/var/www/html'

# Verify that Git is installed:
def git_is_installed():
    '''
    Returns True if a `git` executable is found in the PATH environment
    variable.
    '''
    for path in os.environ['PATH'].split(os.pathsep):
        git_path = os.path.join(path, 'git')
        if os.path.isfile(git_path) and os.access(git_path, os.X_OK):
            return True

    print 'Git is not installed.'
    return False

def update_repo():
    '''
    Creates the local repo if it doesn't exist, or updates it if it does.
    '''
    if not os.path.isdir(LOCAL):
        git.Repo.clone_from(REMOTE, LOCAL)
    else:
        repo = git.Repo(LOCAL)
        repo.remotes.origin.pull()

if __name__ == "__main__":
    if git_is_installed():
        update_repo()
