#!/usr/bin/env python3
import os
import unittest
from types import SimpleNamespace
from unittest import mock

from varscan_tool import varscan as MOD


class ThisTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()


class Test_Varscan2(ThisTestCase):

    CLASS_OBJ = MOD.Varscan2

    def setUp(self):
        super().setUp()

        self.mocks = SimpleNamespace(
            os=mock.MagicMock(spec_set=os),
            SOMATIC=mock.MagicMock(spec_set=MOD.VarscanSomatic),
            PROCESS=mock.MagicMock(spec_set=MOD.SomaticProcess),
        )

        self.somatic_mock = mock.MagicMock(spec_set=MOD.VarscanSomatic)
        self.process_mock = mock.MagicMock(spec_set=MOD.SomaticProcess)

        self.mocks.SOMATIC.return_value = self.somatic_mock
        self.mocks.PROCESS.return_value.__enter__.return_value = self.process_mock

        self.args = SimpleNamespace(
            varscan_jar='varscan_jar',
            min_tumor_freq=0.5,
            max_normal_freq=0.3,
            vps_p_value=0.05,
        )

    def tearDown(self):
        super().tearDown()

    def test_varscan_somatic_called_as_expected(self):
        mpileup = 'foobar'
        idx = 3
        mock_basename = 'base'
        self.mocks.os.path.basename.return_value = mock_basename

        self.CLASS_OBJ.run_pipeline(
            mpileup,
            idx,
            self.args,
            _somatic=self.mocks.SOMATIC,
            _process=self.mocks.PROCESS,
            _di=self.mocks,
        )

        self.mocks.SOMATIC.assert_called_once_with()
        self.somatic_mock.run.assert_called_once_with(
            mpileup, mock_basename,
        )

    def test_varscan_process_somatic_called_as_expected(self):
        mpileup = 'foobar'
        idx = 3
        mock_basename = 'base'
        self.mocks.os.path.basename.return_value = mock_basename

        self.CLASS_OBJ.run_pipeline(
            mpileup,
            idx,
            self.args,
            _somatic=self.mocks.SOMATIC,
            _process=self.mocks.PROCESS,
            _di=self.mocks,
        )

        expected_process_calls = (
            mock.call("{}.snp.vcf".format(mock_basename)),
            mock.call("{}.indel.vcf".format(mock_basename)),
        )

        self.mocks.PROCESS.assert_called_once_with(**vars(self.args))
        self.process_mock.run.assert_has_calls(expected_process_calls)

    def test_varscan_returns_as_expected(self):
        mpileup = 'foobar'
        idx = 3
        mock_basename = 'base'
        self.mocks.os.path.basename.return_value = mock_basename

        expected = MOD.VarscanReturn(
            snp_file="{}.snp.vcf".format(mock_basename),
            indel_file="{}.indel.vcf".format(mock_basename),
            mpileup=mpileup,
            idx=idx,
        )

        found = self.CLASS_OBJ.run_pipeline(
            mpileup,
            idx,
            self.args,
            _somatic=self.mocks.SOMATIC,
            _process=self.mocks.PROCESS,
            _di=self.mocks,
        )
        self.assertEqual(found, expected)


# __END__
