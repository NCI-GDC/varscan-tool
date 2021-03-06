#!/usr/local/env python3
"""
Multithreading VarScan2.3.9

@author: Shenglai Li
"""

import argparse
import concurrent.futures
import logging
import os
import pathlib
import sys
from collections import namedtuple
from types import SimpleNamespace
from typing import List, Optional

from varscan_tool import utils
from varscan_tool.varscan import Varscan2, VarscanReturn
from varscan_tool.varscan_somatic import VarscanSomatic

logger = logging.getLogger(__name__)


DI = SimpleNamespace(futures=concurrent.futures)


def setup_logger():
    """
    Sets up the logger.
    """
    logger_format = "[%(levelname)s] [%(asctime)s] [%(name)s] - %(message)s"
    logger.setLevel(level=logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(logger_format, datefmt="%Y%m%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def tpe_submit_commands(
    args, mpileups, thread_count: int, _varscan=Varscan2, _di=DI
) -> List[VarscanReturn]:
    """run commands on number of threads"""
    varscan_results = []
    with _di.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [
            executor.submit(_varscan.run_pipeline, mpileup, idx, args)
            for idx, mpileup in enumerate(mpileups)
        ]
        for future in _di.futures.as_completed(futures):
            try:
                result = future.result()
                logger.info(result)
                varscan_results.append(result)
            except Exception as e:
                logger.exception(e)
    return varscan_results


def setup_parser() -> argparse.ArgumentParser:
    """
    Loads the parser.
    """
    # Main parser
    parser = argparse.ArgumentParser()
    # Required flags
    parser.add_argument(
        "--pileup",
        action="append",
        dest="pileups",
        required=True,
        help="The mpileup files for tumor/normal pair.",
    )
    parser.add_argument(
        "--ref-dict", required=True, help="reference sequence dictionary file."
    )
    parser.add_argument(
        "--thread-count", type=int, default=2, help="Number of threads."
    )
    parser.add_argument("--java-opts", default="3G", help="JVM -Xmx argument.")
    parser.add_argument(
        "--min-coverage",
        type=int,
        default=8,
        help="Minimum coverage in normal and tumor to call variant (8)",
    )
    parser.add_argument(
        "--min-coverage-normal",
        type=int,
        default=8,
        help="Minimum coverage in normal to call somatic (8)",
    )
    parser.add_argument(
        "--min-coverage-tumor",
        type=int,
        default=6,
        help="Minimum coverage in tumor to call somatic (6)",
    )
    parser.add_argument(
        "--min-var-freq",
        type=float,
        default=0.10,
        help="Minimum variant frequency to call a heterozygote (0.10)",
    )
    parser.add_argument(
        "--min-freq-for-hom",
        type=float,
        default=0.75,
        help="Minimum frequency to call homozygote (0.75)",
    )
    parser.add_argument(
        "--normal-purity",
        type=float,
        default=1.00,
        help="Estimated purity (non-tumor content) of normal sample (1.00)",
    )
    parser.add_argument(
        "--tumor-purity",
        type=float,
        default=1.00,
        help="Estimated purity (tumor content) of tumor sample (1.00)",
    )
    parser.add_argument(
        "--vs-p-value",
        type=float,
        default=0.99,
        help="P-value threshold to call a heterozygote (0.99)",
    )
    parser.add_argument(
        "--somatic-p-value",
        type=float,
        default=0.05,
        help="P-value threshold to call a somatic site (0.05)",
    )
    parser.add_argument(
        "--strand-filter",
        type=int,
        default=0,
        help="If set to 1, removes variants with >0.9 strand bias (0)",
    )
    parser.add_argument(
        "--validation",
        action="store_true",
        help="If set, outputs all compared positions even if non-variant",
    )
    parser.add_argument(
        "--output-vcf",
        type=int,
        default=1,
        help="If set to 1, output VCF instead of VarScan native format",
    )
    parser.add_argument(
        "--min-tumor-freq",
        type=float,
        default=0.10,
        help="Minimun variant allele frequency in tumor [0.10]",
    )
    parser.add_argument(
        "--max-normal-freq",
        type=float,
        default=0.05,
        help="Maximum variant allele frequency in normal [0.05]",
    )
    parser.add_argument(
        "--vps-p-value",
        type=float,
        default=0.07,
        help="P-value for high-confidence calling [0.07]",
    )
    return parser


def run(args, _somatic=VarscanSomatic, _utils=utils):
    """main"""

    # Set class attrs
    _somatic.set_attributes(args)

    varscan_outputs = tpe_submit_commands(args, args.mpileups, args.thread_count)

    # Check outputs
    p = pathlib.Path(".")
    snps = p.glob("*snp.Somatic.hc.vcf")
    indels = p.glob("*indel.Somatic.hc.vcf")

    # Merge
    merged_snps = "multi_varscan2_snp_merged.vcf"
    merged_indels = "multi_varscan2_indel_merged.vcf"
    _utils.merge_outputs(snps, merged_snps)
    _utils.merge_outputs(indels, merged_indels)


def process_argv(argv: Optional[List] = None) -> namedtuple:

    parser = setup_parser()

    if argv:
        args, unknown_args = parser.parse_known_args(argv)
    else:
        args, unknown_args = parser.parse_known_args()

    args_dict = vars(args)
    args_dict['extras'] = unknown_args

    run_args = namedtuple("RunArgs", list(args_dict.keys()))
    return run_args(**args_dict)


def main(argv=None) -> int:

    exit_code = 0
    setup_logger()

    argv = argv or sys.argv
    args = process_argv(argv)
    try:
        run(args)
    except Exception as e:
        logger.exception(e)
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    # CLI Entrypoint.

    ret_code = 0
    try:
        ret_code = main()
    except Exception:
        ret_code = 1

    sys.exit(ret_code)


# __END__
