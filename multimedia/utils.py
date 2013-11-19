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
    _sftp_mkdir(sftp, remote_path)
    sftp.put(local_path, remote_path)
    sftp.close()
    transport.close()


def _sftp_mkdir(sftp, path):
    """
    Create any missing remote directories in the path.
    """
    head = os.path.dirname(path)
    try:
        sftp.stat(head)
    except IOError:
        _sftp_mkdir(sftp, head)
        sftp.mkdir(head)
