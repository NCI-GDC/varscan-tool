#!/usr/bin/env python3

import unittest
from types import SimpleNamespace
from unittest import mock

from varscan_tool import varscan_somatic_process as MOD


class ThisTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mocks = SimpleNamespace(UTILS=mock.MagicMock(spec_set=MOD.utils),)

    def tearDown(self):
        super().tearDown()


class Test_SomaticProcess(ThisTestCase):
    CLASS_OBJ = MOD.SomaticProcess

    def setUp(self):
        super().setUp()
        self.mock_return = MOD.utils.PopenReturn(retcode=0, stdout='foo', stderr='bar',)
        self.mocks.UTILS.call_subprocess.return_value = self.mock_return

    def tearDown(self):
        super().tearDown()

    def test_init_sets_attributes(self):
        args = {
            'varscan_jar': 'varscan',
            'min_tumor_freq': 0.1,
            'max_normal_freq': 0.3,
            'vps_p_value': 0.05,
        }
        obj = self.CLASS_OBJ(**args, _utils=self.mocks.UTILS)
        self.assertEqual(self.mocks.UTILS, obj._utils)
        for k, v in args.items():
            with self.subTest(k=k):
                self.assertEqual(getattr(obj, k), v)

    def test_run_builds_command_as_expected(self):
        args_dict = dict(
            varscan_jar="/path/to/varscan.jar",
            min_tumor_freq=0.1,
            max_normal_freq=0.99,
            vps_p_value=0.05,
        )
        input_vcf = "input.vcf"
        expected_command = self.CLASS_OBJ.COMMAND.format(
            input_vcf=input_vcf, **args_dict
        )
        obj = self.CLASS_OBJ(**args_dict, _utils=self.mocks.UTILS)
        found = obj.run(input_vcf)
        self.mocks.UTILS.call_subprocess.assert_called_once_with(
            expected_command, stdout=MOD.PIPE, stderr=MOD.PIPE,
        )
        self.assertIsNone(found)

    def test_context_run_builds_command_as_expected(self):
        args_dict = dict(
            varscan_jar="/path/to/varscan.jar",
            min_tumor_freq=0.1,
            max_normal_freq=0.99,
            vps_p_value=0.05,
        )
        input_vcf = "input.vcf"
        expected_command = self.CLASS_OBJ.COMMAND.format(
            input_vcf=input_vcf, **args_dict
        )
        with self.CLASS_OBJ(**args_dict, _utils=self.mocks.UTILS) as obj:
            found = obj.run(input_vcf)
        self.mocks.UTILS.call_subprocess.assert_called_once_with(
            expected_command, stdout=MOD.PIPE, stderr=MOD.PIPE,
        )
        self.assertIsNone(found)

    def test_ValueError_raised_on_command_error(self):
        mock_return = MOD.utils.PopenReturn(retcode=1, stdout=None, stderr=None)
        self.mocks.UTILS.call_subprocess.return_value = mock_return
        args_dict = dict(
            varscan_jar="/path/to/varscan.jar",
            min_tumor_freq=0.1,
            max_normal_freq=0.99,
            vps_p_value=0.05,
        )
        input_vcf = "input.vcf"
        obj = self.CLASS_OBJ(**args_dict, _utils=self.mocks.UTILS)
        with self.assertRaisesRegex(ValueError, "command failed"):
            obj.run(input_vcf)

    def test_ValueError_raised_on_command_error_in_context(self):
        mock_return = MOD.utils.PopenReturn(retcode=1, stdout=None, stderr=None)
        self.mocks.UTILS.call_subprocess.return_value = mock_return
        args_dict = dict(
            varscan_jar="/path/to/varscan.jar",
            min_tumor_freq=0.1,
            max_normal_freq=0.99,
            vps_p_value=0.05,
        )
        input_vcf = "input.vcf"
        with self.assertRaisesRegex(ValueError, "command failed"):
            with self.CLASS_OBJ(**args_dict, _utils=self.mocks.UTILS) as obj:
                obj.run(input_vcf)


# __END__
