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
## `opt_path_state`: the directory that contains the state files:
z['opt_path_state'] = '/home/marios/Public/Dropbox/Code/zalza/state'
## `opt_path_build`: the directory in which zBuild logs are saved:
z['opt_path_build'] =  '/home/marios/Public/Dropbox/Code/zalza/build'
## `opt_path_templates`: the directory containing the HTML templates:
z['opt_path_templates'] = '/home/marios/Public/Dropbox/Code/zalza'
## `d_source_skip`: subdirectories of `d_source` to be ignored:
d_source_skip = ['.git']
## `skip_source_files`: files in `d_source` to be ignored:
z['skip_source_files'] = ['.gitignore', 'README.md']
## `generate_output`: whether or not the output will be generated
z['generate_output'] = False
## `site_name`: used as the title in web pages:
z['site_name'] = 'Marios Zindilis'
## `site_base_url`: used in reports and in generation of canonical URLs:
z['site_base_url'] = 'http://zindilis.com'
## `site_author`: the default author, if one is not specified in a source file
z['site_author'] = 'Marios Zindilis'
## `action_index`: serial number of action taken
action_index = 0
## `pages_changed`: list of URLs of pages that were either created or updated
pages_changed = []

p = subprocess.Popen('clear', shell=True)
p.communicate()

build = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
output_buffer = 'zBuild ' + build + '\n'
output_buffer += '=' * len(output_buffer) + '\n\n'

# Traverse source directory:
for traverse_root, traverse_dirs, traverse_files in os.walk(d_source):
    for traverse_dir in traverse_dirs:
        d_section = traverse_root[len(d_source)+1:].split('/')[0]
        # Skip some subdirectories of `d_source`:
        if (traverse_root == d_source 
            and traverse_dir in d_source_skip) \
        or d_section in d_source_skip:
            continue

        z['source_path'] = os.path.join(traverse_root, traverse_dir)
        z['target_path'] = os.path.join(d_htdocs, z['source_path'][len(d_source)+1:])
        z['state_path'] = os.path.join(z['opt_path_state'], z['source_path'][len(d_source)+1:])

        if not os.path.isdir(z['target_path']) or not os.path.isdir(z['state_path']):
            z['generate_output'] = True
            action_index += 1
            output_buffer += ('%s.' % (str(action_index))).ljust(4)
            output_buffer += 'Found a **source directory**:\n\n' 
            output_buffer += '        %s\n\n' % (z['source_path'])

        if not os.path.isdir(z['target_path']):
            os.makedirs(z['target_path'])
            output_buffer += '    Created its **target directory**:\n\n'
            output_buffer += '        %s\n\n' % (z['target_path'])
            os.chdir(d_source)

        if not os.path.isdir(z['state_path']):
            os.makedirs(z['state_path'])
            output_buffer += '    Created its **state directory**:\n\n'
            output_buffer += '        %s\n\n' % (z['state_path'])

    for traverse_file in traverse_files:
        # Skip some files in `d_source`:
        if traverse_root == d_source and traverse_file in z['skip_source_files']:
            continue 
        # Also skip some subdirectories of `d_source`:
        if traverse_root != d_source and traverse_root[len(d_source)+1:].split('/')[0] in d_source_skip:
            continue

        z['source_path'] = os.path.join(traverse_root, traverse_file)
        z['source_content'] = file(z['source_path']).read()
        z['state_path'] = os.path.join(z['opt_path_state'], z['source_path'][len(d_source)+1:]) + '.state'
        
        if not os.path.isfile(z['state_path']) \
        or (os.path.isfile(z['state_path']) and file(z['state_path']).read() != hashlib.md5(z['source_content']).hexdigest()):
            z['generate_output'] = True
            action_index += 1
            output_buffer += ('%s.' % (str(action_index))).ljust(4)
            output_buffer += 'Found a **source file**:\n\n'
            output_buffer += '        %s\n\n' % (z['source_path'])

            if not z['source_path'].endswith('.md'):
                z['target_path'] = os.path.join(d_htdocs, z['source_path'][len(d_source)+1:])
                shutil.copyfile(z['source_path'], z['target_path'])
                output_buffer += '    Copied verbatim at:\n\n'
                output_buffer += '        %s\n\n' % (z['target_path'])

                state_file = open(z['state_path'], 'w')
                state_file.write(hashlib.md5(file(z['source_path']).read()).hexdigest())
                state_file.close()
                output_buffer += '    Created state at:\n\n'
                output_buffer += '        %s\n\n' % (z['state_path'])

            else:
                # Get headers from source file:
                headers = {}
                output_buffer += '    Headers in this file:\n\n'
                for line in file(z['source_path']).readlines():
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.lstrip().rstrip()
                        value = value.lstrip().rstrip()
                        headers[key] = value
                        output_buffer += '        *   %s: %s\n' % (key, headers[key])
                    if line == '- -->\n':
                        output_buffer += '\n'
                        break

                z['page_title'] = z['site_name'] + ' - ' + headers['Title'] if headers.has_key('Title') else z['site_name']
                z['page_section'] = traverse_root[len(d_source)+1:].split('/')[0]
                z['target_path'] = os.path.join(d_htdocs, traverse_root[len(d_source)+1:], os.path.splitext(traverse_file)[0]) + '.html'
                z['canonical_url'] = '/'.join([z['site_base_url'], (os.path.splitext(z['source_path'][len(d_source)+1:])[0] + '.html')])
                target_content = Template(file(os.path.join(z['opt_path_templates'], 'tmpl_header.html')).read()).substitute(z)

                pages_changed.append(z['canonical_url'])

                if z['page_section'] == 'docs':
                    target_content += '<article itemscope itemtype="http://schema.org/Article">'
                elif z['page_section'] == 'blog':
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

                target_file = open(z['target_path'], 'w')
                target_content = htmlmin.minify(target_content, remove_comments=True)
                target_file.write(target_content.encode('utf-8'))
                target_file.close()

                output_buffer += '    Created HTML file at:\n\n'
                output_buffer += '        %s\n\n' % (z['target_path'])

                state_file = open(z['state_path'], 'w')
                state_file.write(hashlib.md5(file(z['source_path']).read()).hexdigest())
                state_file.close()
                output_buffer += '    Create state at:\n\n'
                output_buffer += '        %s\n\n' % (z['state_path'])

            os.chdir(d_source)
            commit_path = z['source_path'][len(d_source)+1:]
            p = subprocess.Popen(['git', 'add', commit_path])
            p.communicate()
            commit_mark = 'zBuild %s' % (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
            p = subprocess.Popen(['git', 'commit', commit_path, '-m', commit_mark, '--quiet'])
            p.communicate()
            p = subprocess.Popen(['git', 'push', '--quiet'])
            p.communicate()
            output_buffer += '    Committed source to Git and pushed.\n\n'

            # Commit the target file:
            os.chdir(d_htdocs)
            commit_path = z['target_path'][len(d_htdocs)+1:]
            p = subprocess.Popen(['git', 'add', commit_path])
            p.communicate()
            commit_mark = 'zBuild %s' % (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
            p = subprocess.Popen(['git', 'commit', commit_path, '-m', commit_mark, '--quiet'])
            p.communicate()
            p = subprocess.Popen(['git', 'push', '--quiet'])
            p.communicate()
            output_buffer += '    Committed target to Git and pushed.\n\n'


if z['generate_output']:
    output_buffer += 'Pages Updated or Created during this Build\n'
    output_buffer += '------------------------------------------\n\n'
    for page_changed in pages_changed:
        output_buffer += '*   %s\n' % (page_changed)

    output_path = os.path.join(z['opt_path_build'], '%s.md' % (build))
    output_file = open(output_path, 'w')
    output_file.write(output_buffer)
    output_file.close()
    output_buffer += '\nThis log has been saved as: %s' % (output_path)
    print output_buffer
