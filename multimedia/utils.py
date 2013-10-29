import os

import paramiko

from .conf import multimedia_settings


def upload_file(local_path, remote_path):
    """
    Given local and remote file paths, upload the local file
    to the remote server using SFTP.
    """
    transport = paramiko.Transport((multimedia_settings.MEDIA_SERVER_HOST,
                                    multimedia_settings.MEDIA_SERVER_PORT))
    transport.connect(username=multimedia_settings.MEDIA_SERVER_USER,
                      password=multimedia_settings.MEDIA_SERVER_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp_mkdir_p(sftp, os.path.dirname(remote_path))
    sftp.put(local_path, remote_path)
    sftp.close()
    transport.close()


def sftp_mkdir_p(sftp, remote_dir):
    """
    """
    if remote_dir == '/':
        sftp.chdir('/')
        return
    if remote_dir == '':
        return
    path, tail = os.path.split(remote_dir)
    sftp_mkdir_p(sftp, path)
    try:
        sftp.chdir(tail)
    except IOError:
        sftp.mkdir(tail)
        sftp.chdir(tail)
