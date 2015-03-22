#!/usr/bin/python -tt
'''
This script traverses a directory of Markdown files and generates static HTML
pages for my website.
'''
import git
import hashlib
import os

REMOTE = 'https://github.com/marios-zindilis/zindilis.com.git'
# LOCAL = '/home/marios/Tests/zindilis.com'
LOCAL = '/var/zalza/zindilis.com'
SKIP_D = ['.git']
SKIP_F = ['.gitignore', 'README.md']
# STATE = '/home/marios/Tests/state'
STATE = '/var/zalza/state'
WEB = '/var/www/html'
DEBUG = True


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


def create_content():
    '''
    Traverses the sources in LOCAL. For directories in LOCAL, it recreates the
    directory structure under WEB and STATE directories. For files in LOCAL, it
    generates HTML if the source file is Markdown, otherwise it copies the file
    verbatim. In both cases, creates the state (MD5 hash of the file).
    '''
    for root, dirs, files in os.walk(LOCAL):
        for current_dir in dirs:
            # The `section` is the first level subdirectory of LOCAL:
            section = root[len(LOCAL)+1:].split('/')[0]
            if (root == LOCAL and current_dir in SKIP_D) or section in SKIP_D:
                continue
            # Absolute and relative paths of source directory:
            source_path_abs = os.path.join(root, current_dir)
            source_path_rel = source_path_abs[len(LOCAL)+1:]

            web_path = os.path.join(WEB, source_path_rel)
            state_path = os.path.join(STATE, source_path_rel)
            if not os.path.isdir(web_path):
                os.makedirs(web_path)
                print 'Created web directory: %s' % (web_path,)
            if not os.path.isdir(state_path):
                os.makedirs(state_path)
                print 'Created state directory: %s' % (state_path,)

        for current_file in files:
            # The `section` is the first level subdirectory of LOCAL:
            section = root[len(LOCAL)+1:].split('/')[0]

            # Skip drafts, skip files in SKIP_F, skip directories in SKIP_D:
            if (current_file.endswith('.draft') or 
            (root == LOCAL and current_file in SKIP_F) or 
            (root != LOCAL and section in SKIP_D)):
                continue

            # Absolute and relative paths of source file:
            source_path_abs = os.path.join(root, current_file)
            source_path_rel = source_path_abs[len(LOCAL)+1:]

            source_content = file(source_path_abs).read()
            source_hash = hashlib.md5(source_content).hexdigest()
            state_path = os.path.join(STATE, source_path_rel) + '.state'

            if (os.path.isfile(state_path) and 
            file(state_path).read() == source_hash):
                continue

            print 'Found source file: %s' % (source_path_abs,)


if __name__ == "__main__":
    if git_is_installed():
        update_repo()
        create_content()
