#!/usr/bin/env python3

from subprocess import PIPE
from textwrap import dedent

from varscan_tool import utils


class SomaticProcess:

    COMMAND = dedent(
        """
        java -d64 -XX:+UseSerialGC -Xmx3G
        -jar {varscan_jar}
        processSomatic {input_vcf}
        --min-tumor-freq {min_tumor_freq}
        --maf-normal-freq {max_normal_freq}
        --p-value {vps_p_value}
        """
    ).strip()

    def __init__(
        self,
        varscan_jar: str,
        min_tumor_freq: float,
        max_normal_freq: float,
        vps_p_value: float,
        _utils=utils,
    ):
        self.varscan_jar = varscan_jar
        self.min_tumor_freq = min_tumor_freq
        self.max_normal_freq = max_normal_freq
        self.vps_p_value = vps_p_value

        self._utils = _utils

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def run(self, input_vcf: str) -> None:
        """run varscan2 workflow"""
        command = self.COMMAND.format(
            varscan_jar=self.varscan_jar,
            input_vcf=input_vcf,
            min_tumor_freq=self.min_tumor_freq,
            max_normal_freq=self.max_normal_freq,
            vps_p_value=self.vps_p_value,
        )
        cmd_return = self._utils.call_subprocess(command, stdout=PIPE, stderr=PIPE)

        if not cmd_return.retcode == 0:
            msg = "varscan processSomatic command failed"
            raise ValueError(msg)

        return


# __END__
