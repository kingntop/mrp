import paramiko, os
from os import path, access, R_OK


class sftpconn(object):

	rsa_private_key = r'/path/to/your/rsa.key'

	def __init__(self, logfile, username, password, host, port, ssh_key):
		paramiko.util.log_to_file(logfile)
		
		print ('Establishing SSH connection to:', host, port, '...')
		self.transport = paramiko.Transport((host, int(port)))

		if ssh_key == True:
			sshkey = paramiko.RSAKey.from_private_key_file(self.rsa_private_key)
			self.transport.connect(username = username, pkey = sshkey)

		else:	
			self.transport.connect(username = username, password = password)

		self.sftp = paramiko.SFTPClient.from_transport(self.transport)
			
	# check if the file exists
	def check_file(self, PATH):
		if path.exists(PATH) and path.isfile(PATH) and access(PATH, R_OK):
			return 0
		else:
			return 1

	# this function will allow the use of wildcards in between underscores, eg: file_*_name.txt
	def is_match(self, a, b):
		aa = a.split('_')
		bb = b.split('_')
		if len(aa) != len(bb): return False
		for x, y in zip(aa, bb):
			if not (x == y or x == '*' or y == '*'): return False
		return True

	
	def get(self, file_formats, local_dir, local_base_dir, remote_dir):
		files_copied = 0
		errors = 0
		summary = ''
		actual_files = []
		remote_files = []
		print ('local_dir:', local_dir)
		print ('local_base_dir:', local_base_dir)
		try:
			for f in self.sftp.listdir(remote_dir):
				remote_files.append(f)

			difference = list(set(remote_files).difference(file_formats))
			# print(difference)
			# for file_format in file_formats:
			for f in difference:
				actual_files.append(remote_dir+f)

			for actual_file in actual_files:
				print ('actual_file:', actual_file)
				base_file = actual_file.replace(remote_dir, '')
				self.sftp.get(actual_file, local_dir + base_file)
				self.sftp.get(actual_file, local_base_dir + base_file)

				files_copied += 1
				summary += "[Copied] " + local_dir + base_file + '\n'

			if errors > 0 or files_copied == 0:
				print ('summary:', summary)
				if files_copied == 0:
					return [summary, "No files available for transfer.", 'No Files']
				else:
					return [summary, "This transaction failed with "+ str(errors) +" error/s:\n\n" + summary, 'Failed']
			else:
				return [summary, "Total file/s copied: %s. Summary: %s" % (str(files_copied), summary), 'Success']

		except Exception as e:
				print ('exception:', e)
				return [summary, "Error while copying file : " + str(e), 'Failed']

	def chdir(self, dir):
    		self.sftp.chdir(dir)

	def ls(self, remote):
		return self.sftp.listdir(remote)

	def close(self):
		if self.transport.is_active():
			self.sftp.close()
			self.transport.close()

	def __enter__(self):
		return self

	def __exit__(self, type, value, tb):
		self.close()

	# def mput(self, local, remote):
	# 	files_copied = 0
	# 	summary = ''
	# 	try:
	# 		for root, dirs, files in os.walk(local):
	# 			print files
	# 			for name in sorted(files):
	# 				filename = os.path.join(root, name)
	# 				self.sftp.put(filename, remote + name)
	# 				files_copied += 1
	# 				summary = summary + "Copied: " + remote + name + "\n"
	# 		return [summary, "Total file/s copied: " + str(files_copied), 'Success']
	# 	except Exception, e:
	# 		return [summary, "Error: " + str(e), 'Failed']

	def mget(self, lfile, local, remote):
		files_copied = 0
		summary = ''
		try:

			for f in self.sftp.listdir(remote):
				print (f)
				self.sftp.get(remote+f, local+f)
				files_copied += 1
				summary = summary + "Copied: " + remote + f + "\n"
			print (summary)
			return [summary, "Total file/s copied: " + str(files_copied), 'Success']
		except Exception as e:
			print (e)
			return [summary, "Error: " + str(e), 'Failed']


