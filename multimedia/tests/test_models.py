from django.test import TestCase


from .factories import EncodeProfileFactory


class EncodeProfileTests(TestCase):
    """
    Test the EncodeProfile model.
    """
    def setUp(self):
        self.profile = EncodeProfileFactory()

    def test_shell_command(self):
        cmd = self.profile.shell_command('/dir/from', '/dir/to')
        self.assertEqual(cmd, ['ffmpeg', '-y', '-i', '/dir/from', '-vn', '/dir/to'])
