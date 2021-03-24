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
import time
from collections import namedtuple
from logging.config import dictConfig
from types import SimpleNamespace
from typing import List, Optional

from varscan_tool import __version__, utils
from varscan_tool.varscan import Varscan2, VarscanReturn
from varscan_tool.varscan_somatic import VarscanSomatic

logger = logging.getLogger(__name__)


DI = SimpleNamespace(futures=concurrent.futures)


def setup_logger():
    """
    Sets up the logger.
    """
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'},
        },
        'handlers': {'default': {'level': 'INFO', 'class': 'logging.StreamHandler',},},
        'loggers': {'': {'handlers': ['default'], 'level': 'INFO', 'propagate': True}},
    }
    dictConfig(config)
    return logger


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


def get_file_size(filename: pathlib.Path) -> int:
    """ Gets file size """
    return filename.stat().st_size


def setup_parser() -> argparse.ArgumentParser:
    """
    Loads the parser.
    """
    # Main parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    # Required flags
    parser.add_argument(
        "--mpileup",
        action="append",
        dest="mpileup",
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
    parser.add_argument(
        "--varscan-jar", default="/usr/local/bin/varscan.jar", required=False,
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        required=False,
        help="Max time for command to run, in seconds.",
    )
    return parser


def run(args, _somatic=VarscanSomatic, _utils=utils):
    """main"""

    # Set class attrs
    _somatic.set_attributes(args)

    varscan_outputs = tpe_submit_commands(args, args.mpileup, args.thread_count)

    # Check outputs
    p = pathlib.Path(".")
    snps = p.glob("*snp.Somatic.hc.vcf")
    indels = p.glob("*indel.Somatic.hc.vcf")

    # Sanity check
    assert (
        len([x for x in snps]) == len([x for x in indels]) == len(args.mpileup)
    ), "Missing output!"
    if any(get_file_size(x) == 0 for x in [x for x in snps] + [x for x in indels]):
        logger.error("Empty output detected!")

    # Merge
    merged_snps = "multi_varscan2_snp_merged.vcf"
    merged_indels = "multi_varscan2_indel_merged.vcf"
    with open(merged_snps, 'w') as fout:
        _utils.merge_outputs(snps, fout)
    with open(merged_indels, 'w') as fout:
        _utils.merge_outputs(indels, fout)


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
    """main"""
    exit_code = 0
    setup_logger()

    argv = argv or sys.argv
    args = process_argv(argv)
    start = time.time()
    try:
        run(args)
        logger.info("Finished, took %s seconds.", round(time.time() - start, 2))
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
