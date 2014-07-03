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
## `opt_path_source`: the directory that contains the source files:
z['opt_path_source']    = '/home/marios/Public/Dropbox/Code/zindilis.com'
## `opt_path_target`: the directory served over HTTP:
z['opt_path_target']	= '/home/marios/Public/Dropbox/Code/marios-zindilis.github.io'
## `opt_path_state`: the directory that contains the state files:
z['opt_path_state']     = '/home/marios/Public/Dropbox/Code/zalza/state'
## `opt_path_build`: the directory in which zBuild logs are saved:
z['opt_path_build']	= '/home/marios/Public/Dropbox/Code/zalza/build'
## `opt_path_templates`: the directory containing the HTML templates:
z['opt_path_templates'] = '/home/marios/Public/Dropbox/Code/zalza'
## `skip_source_dirs`: subdirectories of `opt_path_source` to be ignored:
z['skip_source_dirs']	= ['.git', 'state']
## `skip_source_files`: files in `opt_path_source` to be ignored:
z['skip_source_files'] 	= ['.gitignore', 'README.md']
## `generate_output`: whether or not the output will be generated
z['generate_output']	= False
## `site_name`: used as the title in web pages:
z['site_name']          = 'Marios Zindilis'
## `site_base_url`: used in reports and in generation of canonical URLs:
z['site_base_url']      = 'http://zindilis.com'
## `site_author`: the default author, if one is not specified in a source file
z['site_author']        = 'Marios Zindilis'
## `action_index`: serial number of action taken
action_index = 0

p = subprocess.Popen('clear', shell=True)
p.communicate()

build = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
output_buffer = 'zBuild ' + build + '\n'
output_buffer += '=' * len(output_buffer) + '\n\n'

for traverse_root, traverse_dirs, traverse_files in os.walk(z['opt_path_source']):
	for traverse_dir in traverse_dirs:
		# Skip some subdirectories of `opt_path_source`:
		if traverse_root == z['opt_path_source'] and traverse_dir in z['skip_source_dirs']:
			continue
		# Also skip their subdirectories:
		if traverse_root != z['opt_path_source'] and traverse_root[len(z['opt_path_source'])+1:].split('/')[0] in z['skip_source_dirs']:
			continue

		z['source_path'] = os.path.join(traverse_root, traverse_dir)
		z['target_path'] = os.path.join(z['opt_path_target'], z['source_path'][len(z['opt_path_source'])+1:])
		z['state_path'] = os.path.join(z['opt_path_state'], z['source_path'][len(z['opt_path_source'])+1:])

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
			os.chdir(z['opt_path_source'])

		if not os.path.isdir(z['state_path']):
			os.makedirs(z['state_path'])
			output_buffer += '    Created its **state directory**:\n\n'
			output_buffer += '        %s\n\n' % (z['state_path'])

	for traverse_file in traverse_files:
		# Skip some files in `opt_path_source`:
		if traverse_root == z['opt_path_source'] and traverse_file in z['skip_source_files']:
			continue 
		# Also skip some subdirectories of `opt_path_source`:
		if traverse_root != z['opt_path_source'] and traverse_root[len(z['opt_path_source'])+1:].split('/')[0] in z['skip_source_dirs']:
			continue

		z['source_path'] = os.path.join(traverse_root, traverse_file)
		z['source_content'] = file(z['source_path']).read()
		z['state_path'] = os.path.join(z['opt_path_state'], z['source_path'][len(z['opt_path_source'])+1:]) + '.state'
		
		if not os.path.isfile(z['state_path']) \
		or (os.path.isfile(z['state_path']) and file(z['state_path']).read() != hashlib.md5(z['source_content']).hexdigest()):
			z['generate_output'] = True
			action_index += 1
			output_buffer += ('%s.' % (str(action_index))).ljust(4)
			output_buffer += 'Found a **source file**:\n\n'
			output_buffer += '        %s\n\n' % (z['source_path'])

			if not z['source_path'].endswith('.md'):
				z['target_path'] = os.path.join(z['opt_path_target'], z['source_path'][len(z['opt_path_source'])+1:])
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
				z['page_section'] = traverse_root[len(z['opt_path_source'])+1:].split('/')[0]
				z['target_path'] = os.path.join(z['opt_path_target'], traverse_root[len(z['opt_path_source'])+1:], os.path.splitext(traverse_file)[0]) + '.html'
				z['canonical_url'] = '/'.join([z['site_base_url'], (os.path.splitext(z['source_path'][len(z['opt_path_source'])+1:])[0] + '.html')])
				target_content = Template(file(os.path.join(z['opt_path_templates'], 'tmpl_header.html')).read()).substitute(z)

				if z['page_section'] == 'docs':
					target_content += '<article itemscope itemtype="http://schema.org/Article">'
				elif z['page_section'] == 'blog':
					target_content += '<article itemscope itemtype="http://schema.org/BlogPosting">'
				else:
					target_content += '<article>'
				target_content += markdown2.markdown(file(z['source_path']).read().decode('utf-8'), extras=['fenced-code-blocks'])
				
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
				
				target_content += Template(file(os.path.join(z['opt_path_templates'], 'tmpl_footer.html')).read()).substitute(z)

				target_file = open(z['target_path'], 'w')
				if z['target_path'].endswith('.el.html'):
					target_file.write(target_content.encode('utf-8'))
				else:
					target_file.write(htmlmin.minify(target_content, remove_comments=True))
				target_file.close()

				output_buffer += '    Created HTML file at:\n\n'
				output_buffer += '        %s\n\n' % (z['target_path'])

				state_file = open(z['state_path'], 'w')
				state_file.write(hashlib.md5(file(z['source_path']).read()).hexdigest())
				state_file.close()
				output_buffer += '    Create state at:\n\n'
				output_buffer += '        %s\n\n' % (z['state_path'])

			os.chdir(z['opt_path_source'])
			commit_path = z['source_path'][len(z['opt_path_source'])+1:]
			p = subprocess.Popen(['git', 'add', commit_path])
			p.communicate()
			commit_mark = 'zBuild %s' % (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
			p = subprocess.Popen(['git', 'commit', commit_path, '-m', commit_mark, '--quiet'])
			p.communicate()
			p = subprocess.Popen(['git', 'push', '--quiet'])
			p.communicate()
			output_buffer += '    Committed source to Git and pushed.\n\n'

			# Commit the target file:
			os.chdir(z['opt_path_target'])
			commit_path = z['target_path'][len(z['opt_path_target'])+1:]
			p = subprocess.Popen(['git', 'add', commit_path])
			p.communicate()
			commit_mark = 'zBuild %s' % (datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
			p = subprocess.Popen(['git', 'commit', commit_path, '-m', commit_mark, '--quiet'])
			p.communicate()
			p = subprocess.Popen(['git', 'push', '--quiet'])
			p.communicate()
			output_buffer += '    Committed target to Git and pushed.\n\n'


if z['generate_output']:
	output_path = os.path.join(z['opt_path_build'], '%s.md' % (build))
	output_file = open(output_path, 'w')
	output_file.write(output_buffer)
	output_file.close()
	output_buffer += 'This log has been saved as: %s' % (output_path)
	print output_buffer
