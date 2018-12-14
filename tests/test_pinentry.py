
import unittest

import mock as unittest_mock

import pysectools
import pysectools.pinentry


class TestPinentry(unittest.TestCase):
    @unittest_mock.patch('pysectools.pinentry.subprocess')
    @unittest_mock.patch('pysectools.pinentry.cmd_exists')
    @unittest_mock.patch('pysectools.pinentry.os.isatty')
    def test_no_pinentry_no_tty(
            self,
            mock_os_isatty,
            mock_cmd_exists,
            mock_subprocess,
    ):
        """ What happens when pinentry missing and tty missing
        """
        mock_cmd_exists.return_value = False
        mock_os_isatty.return_value = False
        with self.assertRaises(
                pysectools.pinentry.PinentryUnavailableException,
        ):
            pysectools.pinentry.Pinentry(
                fallback_to_getpass=True,
            )
            self.assertTrue(False, 'we missing an exception')
        mock_subprocess.Popen.assert_not_called()


    @unittest_mock.patch('pysectools.pinentry.subprocess')
    @unittest_mock.patch('pysectools.pinentry.cmd_exists')
    @unittest_mock.patch('pysectools.pinentry.os.isatty')
    def test_no_pinentry_no_tty_no_fallback(
            self,
            mock_os_isatty,
            mock_cmd_exists,
            mock_subprocess,
    ):
        """ What happens when pinentry missing and tty missing
            And program declines getpass fall back
        """
        mock_cmd_exists.return_value = False
        mock_os_isatty.return_value = False
        with self.assertRaises(
                pysectools.pinentry.PinentryUnavailableException,
        ):
            pysectools.pinentry.Pinentry(
                fallback_to_getpass=False,
            )
            self.assertTrue(False, 'we missing an exception')
        mock_subprocess.Popen.assert_not_called()


    @unittest_mock.patch('pysectools.pinentry.subprocess')
    @unittest_mock.patch('pysectools.pinentry.cmd_exists')
    @unittest_mock.patch('pysectools.pinentry.os.isatty')
    def test_no_pinentry_with_fake_tty(
            self,
            mock_os_isatty,
            mock_cmd_exists,
            mock_subprocess,
    ):
        """ What happens when pinentry is missing and tty
            is accepted
        """
        mock_cmd_exists.return_value = False
        mock_os_isatty.return_value = True
        pinentry = pysectools.pinentry.Pinentry(
            fallback_to_getpass=True,
        )
        self.assertEqual(
            pinentry._ask,
            pinentry._ask_with_getpass,
        )


    @unittest_mock.patch('pysectools.pinentry.subprocess')
    @unittest_mock.patch('pysectools.pinentry.cmd_exists')
    def test_with_pinentry(
            self,
            mock_cmd_exists,
            mock_subprocess,
    ):
        """ What happens with pinentry
        """
        mock_cmd_exists.return_value = True
        pinentry = pysectools.pinentry.Pinentry()
        self.assertEqual(
            pinentry.process,
            mock_subprocess.Popen.return_value,
        )

    @unittest_mock.patch('pysectools.pinentry.subprocess')
    @unittest_mock.patch('pysectools.pinentry.cmd_exists')
    def test_custom_pinentry(
            self,
            mock_cmd_exists,
            mock_subprocess,
    ):
        """ What happens with custom pinentry
        """
        mock_cmd_exists.return_value = True
        pysectools.pinentry.Pinentry(
            pinentry_path='/fakefs/bin/pinentry-fake'
        )
        mock_subprocess.Popen.assert_called_once_with(
            '/fakefs/bin/pinentry-fake',
            close_fds=True,
            stderr=mock_subprocess.STDOUT,
            stdin=mock_subprocess.PIPE,
            stdout=mock_subprocess.PIPE,
        )

