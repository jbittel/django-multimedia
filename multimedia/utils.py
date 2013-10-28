import paramiko

from .conf import multimedia_settings


def upload_file(local_file, remote_file):
    """
    Given local and remote file paths, upload the local file
    to the remote server using SFTP.
    """
    transport = paramiko.Transport((multimedia_settings.MEDIA_SERVER_HOST,
                                    multimedia_settings.MEDIA_SERVER_PORT))
    transport.connect(username=multimedia_settings.MEDIA_SERVER_USER,
                      password=multimedia_settings.MEDIA_SERVER_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(local_file, remote_file)
    sftp.close()
    transport.close()
