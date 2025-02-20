#!/usr/bin/env python3

import unittest
from types import SimpleNamespace
from unittest import mock

from varscan_tool import varscan_somatic as MOD


class ThisTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mocks = SimpleNamespace(UTILS=mock.MagicMock(spec_set=MOD.utils))

    def tearDown(self):
        super().tearDown()


class Test_VarscanSomatic(ThisTestCase):
    CLASS_OBJ = MOD.VarscanSomatic

    def setUp(self):
        super().setUp()

        self.attrs = {
            "java_opts": "java_opts",
            "varscan_jar": "varscan.jar",
            "min_coverage": 2,
            "min_coverage_normal": 3,
            "min_coverage_tumor": 4,
            "min_var_freq": 0.2,
            "min_freq_for_hom": 0.3,
            "normal_purity": 0.5,
            "tumor_purity": 0.6,
            "vs_p_value": 0.05,
            "somatic_p_value": 0.8,
            "strand_filter": 0,
            "validation": False,
            "output_vcf": 1,
        }
        self.process_return = MOD.utils.PopenReturn(
            retcode=0, stdout="stdout", stderr="stderr"
        )
        self.mocks.UTILS.call_subprocess.return_value = self.process_return

    def tearDown(self):
        super().tearDown()
        self.CLASS_OBJ.set_attributes()

    def test_set_attributes_sets_for_instances(self):
        self.CLASS_OBJ.set_attributes(SimpleNamespace(**self.attrs))

        obj_a = self.CLASS_OBJ()
        obj_b = self.CLASS_OBJ()

        for attr, value in self.attrs.items():
            with self.subTest(attr=attr):
                self.assertEqual(value, getattr(obj_a, attr))
                self.assertEqual(value, getattr(obj_b, attr))

    def test_subprocess_called_with_expected_command(self):
        self.CLASS_OBJ.set_attributes(SimpleNamespace(**self.attrs))

        attrs = self.attrs.copy()
        attrs["validation"] = ""
        timeout = None
        output_base = "out"
        mpileup = "mpileup"
        attrs.update({"output_base": output_base, "mpileup": mpileup})

        expected_cmd = self.CLASS_OBJ.COMMAND.format(**attrs)
        obj = self.CLASS_OBJ(_utils=self.mocks.UTILS)
        obj.run(mpileup, output_base)

        self.mocks.UTILS.call_subprocess.assert_called_once_with(
            expected_cmd,
            timeout,
            stdout=MOD.PIPE,
            stderr=MOD.PIPE,
        )

    def test_run_raises_ValueError_with_failed_command(self):
        self.CLASS_OBJ.set_attributes(SimpleNamespace(**self.attrs))
        subprocess_return = MOD.utils.PopenReturn(retcode=1, stdout="", stderr="")
        self.mocks.UTILS.call_subprocess.return_value = subprocess_return

        output_base = "out"
        mpileup = "mpileup"

        obj = self.CLASS_OBJ(_utils=self.mocks.UTILS)
        with self.assertRaisesRegex(ValueError, "somatic command failed"):
            obj.run(mpileup, output_base)


# __END__
