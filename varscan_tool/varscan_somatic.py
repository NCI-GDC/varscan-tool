#!/usr/bin/env python3

import os
from subprocess import PIPE
from textwrap import dedent
from types import SimpleNamespace

from varscan_tool import utils

DI = SimpleNamespace(os=os)


class VarscanSomatic:
    COMMAND = dedent(
        """
        java -d64 -XX:+UseSerialGC
        -Xmx{java_opts}
        -jar {varscan_jar}
        somatic {mpileup} {output_base}
        --mpileup 1
        --min-coverage {min_coverage}
        --min-coverage-normal {min_coverage_normal}
        --min-coverage-tumor {min_coverage_tumor}
        --min-var-freq {min_var_freq}
        --min-freq-for-hom {min_freq_for_hom}
        --normal-purity {normal_purity}
        --tumor-purity {tumor_purity}
        --p-value {vs_p_value}
        --somatic-p-value {somatic_p_value}
        --strand-filter {strand_filter}
        --output-vcf {output_vcf}
        {validation}
        """
    ).strip()

    ATTRS = (
        "java_opts",
        "varscan_jar",
        "min_coverage",
        "min_coverage_normal",
        "min_coverage_tumor",
        "min_var_freq",
        "min_freq_for_hom",
        "normal_purity",
        "tumor_purity",
        "vs_p_value",
        "somatic_p_value",
        "strand_filter",
        "validation",
        "output_vcf",
    )

    def __init__(self, _utils=utils):
        self._utils = _utils

    @classmethod
    def set_attributes(cls, args=None):
        for attr in cls.ATTRS:
            setattr(cls, attr, getattr(args, attr, None))

    def run(
        self, mpileup: str, output_base: str,
    ):
        """run varscan2 workflow"""
        command = self.COMMAND.format(
            java_opts=self.java_opts,
            varscan_jar=self.varscan_jar,
            mpileup=mpileup,
            output_base=output_base,
            min_coverage=self.min_coverage,
            min_coverage_normal=self.min_coverage_normal,
            min_coverage_tumor=self.min_coverage_tumor,
            min_var_freq=self.min_var_freq,
            min_freq_for_hom=self.min_freq_for_hom,
            normal_purity=self.normal_purity,
            tumor_purity=self.tumor_purity,
            vs_p_value=self.vs_p_value,
            somatic_p_value=self.somatic_p_value,
            strand_filter=self.strand_filter,
            output_vcf=self.output_vcf,
            validation='--validation' if self.validation else '',
        )
        cmd_return = self._utils.call_subprocess(command, stdout=PIPE, stderr=PIPE)
        if not cmd_return.retcode == 0:
            msg = "Varscan somatic command failed"
            raise ValueError(msg, command)
        return


# __END__
