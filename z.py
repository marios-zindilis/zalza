#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import datetime
import hashlib
import htmlmin
import markdown2
import os
import shutil
import subprocess
from string import Template

# # Configurable options:
z = {}
## `d_source`: the directory that contains the source files:
d_source = '/home/marios/Public/Dropbox/Code/zindilis.com'
## `d_htdocs`: the directory served over HTTP:
d_htdocs = '/home/marios/Public/Dropbox/Code/marios-zindilis.github.io'
## `d_state`: the directory that contains the state files:
d_state = '/home/marios/Public/Dropbox/Code/zalza/state'
## `opt_path_build`: the directory in which zBuild logs are saved:
z['opt_path_build'] =  '/home/marios/Public/Dropbox/Code/zalza/build'
## `opt_path_templates`: the directory containing the HTML templates:
z['opt_path_templates'] = '/home/marios/Public/Dropbox/Code/zalza'
## `d_source_skip`: subdirectories of `d_source` to be ignored:
d_source_skip = ['.git']
## `f_source_skip`: files in `d_source` to be ignored:
f_source_skip = ['.gitignore', 'README.md']
## `repaginate`: whether or not to recreate blog pagination:
repaginate = False
## `site_name`: used as the title in web pages:
z['site_name'] = 'Marios Zindilis'
## `site_base_url`: used in reports and in generation of canonical URLs:
z['site_base_url'] = 'http://zindilis.com'
## `site_author`: the default author, if one is not specified in a source file
z['site_author'] = 'Marios Zindilis'
## `action_index`: serial number of action taken
action_index = 0
## `changes`: list of directories or files that were either created or updated
changes = []

# p = subprocess.Popen('clear', shell=True)
# p.communicate()
subprocess.Popen('clear', shell=True).communicate()

build = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
output = 'zBuild ' + build + '\n'
output += '=' * len(output) + '\n\n'

def get_headers(source_path):
    headers = {}
    for line in file(source_path).readlines():
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.lstrip().rstrip()
            value = value.lstrip().rstrip()
            headers[key] = value
        if line == '- -->\n':
            break
    return headers

# Traverse source directory:
for traverse_root, traverse_dirs, traverse_files in os.walk(d_source):
    for traverse_dir in traverse_dirs:
        d_section = traverse_root[len(d_source)+1:].split('/')[0]
        # Skip some subdirectories of `d_source`:
        if (traverse_root == d_source 
            and traverse_dir in d_source_skip) \
        or d_section in d_source_skip:
            continue

        # The source_path is the absolute path of the source directory:
        source_path = os.path.join(traverse_root, traverse_dir)
        # The source_subpath is the portion of the source_path after the base 
        # source directory. It is used to recreate the exact same directory 
        # structure from the source to the target and state directories.
        source_subpath = source_path[len(d_source)+1:]
        target_path = os.path.join(d_htdocs, source_subpath)
        state_path = os.path.join(d_state, source_subpath)

        if not os.path.isdir(target_path) or not os.path.isdir(state_path):
            action_index += 1
            output += ('%s.' % (str(action_index))).ljust(4)
            output += 'Found a **source directory**:\n\n' 
            output += '        %s\n\n' % (source_path)

        if not os.path.isdir(target_path):
            os.makedirs(target_path)
            output += '    Created its **target directory**:\n\n'
            output += '        %s\n\n' % (target_path)
            os.chdir(d_source)

        if not os.path.isdir(state_path):
            os.makedirs(state_path)
            output += '    Created its **state directory**:\n\n'
            output += '        %s\n\n' % (state_path)

    for traverse_file in traverse_files:
        # Skip files that end in '.draft':
        if traverse_file.endswith('.draft'):
            continue
        d_section = traverse_root[len(d_source)+1:].split('/')[0]
        # Skip some files in `d_source`:
        if traverse_root == d_source and traverse_file in f_source_skip:
            continue 
        # Also skip some subdirectories of `d_source`:
        if traverse_root != d_source and d_section in d_source_skip:
            continue

        # The source_path is the absolute path of the source file:
        source_path = os.path.join(traverse_root, traverse_file)
        # The source_subpath is the portion of the source_path after the base 
        # source directory. It is used to create the target file and the state  
        # file under the same directory structure from the source to the target 
        # and state directories:
        source_subpath = source_path[len(d_source)+1:]
        z['source_content'] = file(source_path).read()
        source_hash = hashlib.md5(z['source_content']).hexdigest()

        state_path = os.path.join(d_state, source_subpath)
        state_path = state_path + '.state'
        
        # If the state file does not exist (which means that the source file 
        # is new), or the state file does exist but the hash of the content is 
        # not the same as the contents of the state file (which means that the 
        # source file has changed), then [re-]generate the target file: 
        if not os.path.isfile(state_path) \
        or (os.path.isfile(state_path) and \
        file(state_path).read() != source_hash):
            action_index += 1
            output += ('%s.' % (str(action_index))).ljust(4)
            output += 'Found a **source file**:\n\n'
            output += '        %s\n\n' % (source_path)

            # If the source is not a Markdown file, then just copy it verbatim 
            # to the target directory and [re-]create the state:
            if not source_path.endswith('.md'):
                target_path = os.path.join(d_htdocs, source_subpath)
                shutil.copyfile(source_path, target_path)
                output += '    Copied verbatim at:\n\n'
                output += '        %s\n\n' % (target_path)

                state_file = open(state_path, 'w')
                state_file.write(source_hash)
                state_file.close()
                output += '    Created state at:\n\n'
                output += '        %s\n\n' % (state_path)
            # Otherwise, if the source _is_ Markdown, then [re-]create both the
            # HTML output and the state:
            else:
                # Get headers from source file:
                headers = get_headers(source_path)
                output += '    Headers in this file:\n\n'
                for header in headers.keys():
                    output += '        *   %s: %s\n' % (header, headers[header])
                output += '\n'

                tmpl = {}
                tmpl['site_name'] = z['site_name']
                tmpl['page_title'] = z['site_name']
                if headers.has_key('Title'):
                    tmpl['page_title'] += ' - %s' % (headers['Title'])
                if headers.has_key('Description'):
                    tmpl['description'] = headers['Description']
                elif headers.has_key('Title'):
                    tmpl['description'] = headers['Title']
                else:
                    tmpl['description'] = z['site_name']
                target_path = os.path.join(d_htdocs, traverse_root[len(d_source)+1:], os.path.splitext(traverse_file)[0]) + '.html'
                tmpl['canonical_url'] = '/'.join([z['site_base_url'], (os.path.splitext(source_subpath)[0] + '.html')])
                target_content = Template(file(os.path.join(z['opt_path_templates'], 'tmpl_header.html')).read()).substitute(tmpl)

                changes.append(tmpl['canonical_url'])

                if d_section == 'docs':
                    target_content += '<article itemscope itemtype="http://schema.org/Article">'
                elif d_section == 'blog':
                    if not source_path.endswith('index.md'):
                        repaginate = True
                    target_content += '<article itemscope itemtype="http://schema.org/BlogPosting">'
                else:
                    target_content += '<article>'
                
                target_content = target_content.decode('utf-8')
                target_content += markdown2.markdown(z['source_content'], extras=['fenced-code-blocks'])
                
                z['page_info'] = ''
                if headers.has_key('Title'):
                    z['page_info'] += '<li>Title: <span itemprop="name">%s</span></li>\n' % (headers['Title'])
                if headers.has_key('Author'):
                    z['page_info'] += '<li>Author: <span itemprop="author">%s</span></li>\n' % (headers['Author'])
                else:
                    z['page_info'] += '<li>Author: <span itemprop="author">%s</span></li>\n' % (z['site_author'])
                if headers.has_key('Editor'):
                    z['page_info'] += '<li>Editor: <span itemprop="editor">%s</span></li>\n' % (headers['Editor'])
                if headers.has_key('First Published'):
                    z['page_info'] += '<li>First Published: <meta itemprop="datePublished" content="%s">%s</li>\n' % (headers['First Published'], headers['First Published'])
                if headers.has_key('Last Updated'):
                    z['page_info'] += '<li>Last Updated: <meta itemprop="dateModified" content="%s">%s</li>\n' % (headers['Last Updated'], headers['Last Updated'])
                
                page_footer = Template(file(os.path.join(z['opt_path_templates'], 'tmpl_footer.html')).read()).substitute(z)
                page_footer = page_footer.decode('utf-8')
                target_content += page_footer

                target_file = open(target_path, 'w')
                target_content = htmlmin.minify(target_content, remove_comments=True)
                target_file.write(target_content.encode('utf-8'))
                target_file.close()

                output += '    Created HTML file at:\n\n'
                output += '        %s\n\n' % (target_path)

                state_file = open(state_path, 'w')
                state_file.write(source_hash)
                state_file.close()
                output += '    Create state at:\n\n'
                output += '        %s\n\n' % (state_path)

            os.chdir(d_source)
            commit_path = source_subpath
            p = subprocess.Popen(['git', 'add', commit_path])
            p.communicate()
            commit_mark = 'zBuild %s' % (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
            p = subprocess.Popen(['git', 'commit', commit_path, '-m', commit_mark, '--quiet'])
            p.communicate()
            p = subprocess.Popen(['git', 'push', '--quiet'])
            p.communicate()
            output += '    Committed source to Git and pushed.\n\n'

            # Commit the target file:
            os.chdir(d_htdocs)
            commit_path = target_path[len(d_htdocs)+1:]
            p = subprocess.Popen(['git', 'add', commit_path])
            p.communicate()
            commit_mark = 'zBuild %s' % (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
            p = subprocess.Popen(['git', 'commit', commit_path, '-m', commit_mark, '--quiet'])
            p.communicate()
            p = subprocess.Popen(['git', 'push', '--quiet'])
            p.communicate()
            output += '    Committed target to Git and pushed.\n\n'

if repaginate:
    posts = {}
    pages = {}
    post = 0
    page = 0
    d_blog = os.path.join(d_source, 'blog')
    for traverse_root, traverse_dirs, traverse_files in os.walk(d_blog):
        for traverse_file in traverse_files:
            if traverse_file.endswith('.md'):
                source_path = os.path.join(traverse_root, traverse_file)
                source_path_date = get_headers(source_path)['First Published']
                posts[source_path_date] = source_path
    for date_published in sorted(posts.keys(), reverse=True):
        if post == 0:
            pages[page] = {}
        pages[page][post] = posts[date_published]
        post += 1
        if post == 10:
            post = 0
            page += 1
    for page in sorted(pages.keys()):
        d = {}
        d['site_name'] = z['site_name']
        d['canonical_url'] = ''
        if page == 0:
            d['canonical_url'] = z['site_base_url'] + '/'
            target_d = d_htdocs
            target_f = os.path.join(target_d, 'index.html')
            d['page_title'] = z['site_name']
        else:
            d['canonical_url'] = '/'.join([z['site_base_url'], 'page', '%d.html' % (page)])
            target_d = os.path.join(d_htdocs, 'page')
            target_f = os.path.join(target_d, '%d.html' % (page))
            d['page_title'] = '%s - Page %d' % (z['site_name'], page)
        d['description'] = d['page_title']
        commit_f = target_f[len(target_d)+1:]
        target_f = open(target_f, 'w')

        target_content = Template(file(os.path.join(z['opt_path_templates'], 'tmpl_header.html')).read()).substitute(d)

        for post in sorted(pages[page].keys()):
            headers = get_headers(pages[page][post])
            target_content += '<article itemscope itemtype="http://schema.org/BlogPosting">'
            href = os.path.splitext(pages[page][post][len(d_source):])[0] + '.html'
            target_content += '<h1><a href="%s">%s</a></h1>' % (href, headers['Title'])
            temp_content = file(pages[page][post]).read()
            temp_content = temp_content.decode('utf-8')
            temp_content = markdown2.markdown(temp_content, extras=['fenced-code-blocks'])
            skip_lines = False
            for line in temp_content.split('\n'):
                if line.startswith('<h1>'):
                    continue
                if line.startswith('<ol class=') and 'breadcrumb' in line:
                    skip_lines = True
                    continue
                if skip_lines and line.startswith('</ol>'):
                    skip_lines = False
                    continue
                if skip_lines:
                    continue
                target_content += '%s\n' % (line.encode('utf-8'))
            target_content += '<footer><span class="glyphicon glyphicon-time"></span> Posted on %s</footer>' % (headers['First Published'])
            target_content += '</article>'

        target_content += '<ul class="pagination">'
        if page == 0:
            target_content += '<li class="disabled"><a href="#">Previous</a></li>'
        elif page == 1:
            target_content += '<li><a href="/">Previous</a></li>'
        else:
            target_content += '<li><a href="/page/%d.html">Previous</a></li>' % (page - 1)

        for page_link in sorted(pages.keys()):
            if page_link == 0:
                if page == 0:
                    target_content += '<li class="active"><a href="/">0</a></li>'
                else:
                    target_content += '<li><a href="/">0</a></li>'
            else:
                if page == page_link:
                    target_content += '<li class="active"><a href="/page/%d.html">%d</a></li>' % (page_link, page_link)
                else:
                    target_content += '<li><a href="/page/%d.html">%d</a></li>' % (page_link, page_link)

        if page == (len(pages.keys()) - 1):
            target_content += '<li class="disabled"><a href="#">Next</a></li>'
        else:
            target_content += '<li><a href="/page/%d.html">Next</a></li>' % (page + 1)

        target_content += '</ul>'

        target_f.write(target_content)
        target_f.close()

        os.chdir(target_d)
        p = subprocess.Popen(['git', 'add', commit_f])
        p.communicate()
        commit_mark = 'zBuild %s' % (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
        p = subprocess.Popen(['git', 'commit', commit_f, '-m', commit_mark, '--quiet'])
        p.communicate()
        p = subprocess.Popen(['git', 'push', '--quiet'])
        p.communicate()


if len(changes):
    output += 'Changes during this Build\n'
    output += '-------------------------\n\n'
    for change in changes:
        output += '*   %s\n' % (change)

    output_path = os.path.join(z['opt_path_build'], '%s.md' % (build))
    output_file = open(output_path, 'w')
    output_file.write(output)
    output_file.close()
    output += '\nThis log has been saved as: %s' % (output_path)
    print output
