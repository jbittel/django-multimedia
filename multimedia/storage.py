from django.core.files.storage import FileSystemStorage


class OverwritingStorage(FileSystemStorage):
    """
    File storage backend that overwrites existing files when the
    replacement file has the same name.
    """
    def get_available_name(self, name):
        return name

    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super(OverwritingStorage, self)._save(name, content)
