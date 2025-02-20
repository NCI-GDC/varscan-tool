#!/usr/bin/env python3
import logging
import os
from types import SimpleNamespace
from typing import NamedTuple

from varscan_tool import utils
from varscan_tool.varscan_somatic import VarscanSomatic
from varscan_tool.varscan_somatic_process import SomaticProcess

DI = SimpleNamespace(os=os)
logger = logging.getLogger(__name__)


class VarscanReturn(NamedTuple):
    snp_file: str
    indel_file: str
    mpileup: str
    idx: int


class Varscan2:
    @staticmethod
    def run_pipeline(
        mpileup: str,
        idx: int,
        args,
        _somatic=VarscanSomatic,
        _process=SomaticProcess,
        _di=DI,
    ) -> VarscanReturn:
        output_base = _di.os.path.basename(mpileup)

        varscan_somatic = _somatic()
        varscan_somatic.run(mpileup, output_base)

        snp_file = "{}.snp.vcf".format(output_base)
        indel_file = "{}.indel.vcf".format(output_base)

        with _process(
            args.timeout,
            args.varscan_jar,
            args.min_tumor_freq,
            args.max_normal_freq,
            args.vps_p_value,
        ) as process:
            process.run(snp_file)
            process.run(indel_file)

        return VarscanReturn(
            snp_file=snp_file,
            indel_file=indel_file,
            mpileup=mpileup,
            idx=idx,
        )


# __END__
