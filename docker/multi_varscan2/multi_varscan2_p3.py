"""
Multithreading VarScan2.3.9

@author: Shenglai Li
"""

import os
import sys
import time
import glob
import ctypes
import logging
import argparse
import threading
import subprocess
from signal import SIGKILL
from functools import partial
from concurrent.futures import ThreadPoolExecutor


def setup_logger():
    """
    Sets up the logger.
    """
    logger = logging.getLogger("multi_varscan2")
    logger_format = "[%(levelname)s] [%(asctime)s] [%(name)s] - %(message)s"
    logger.setLevel(level=logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(logger_format, datefmt="%Y%m%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def subprocess_commands_pipe(cmd, logger, shell_var=True, lock=threading.Lock()):
    """run pool commands"""
    libc = ctypes.CDLL("libc.so.6")
    pr_set_pdeathsig = ctypes.c_int(1)

    def child_preexec_set_pdeathsig():
        """
        preexec_fn argument for subprocess.Popen,
        it will send a SIGKILL to the child once the parent exits
        """

        def pcallable():
            return libc.prctl(pr_set_pdeathsig, ctypes.c_ulong(SIGKILL))

        return pcallable

    try:
        output = subprocess.Popen(
            cmd,
            executable="/bin/bash",
            shell=shell_var,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=child_preexec_set_pdeathsig(),
        )
        ret = output.wait()
        with lock:
            logger.info("Running command: %s", cmd)
    except BaseException as e:
        output.kill()
        with lock:
            logger.error("command failed %s", cmd)
            logger.exception(e)
    finally:
        output_stdout, output_stderr = output.communicate()
        with lock:
            logger.error(output_stdout.decode("UTF-8"))
            logger.error(output_stderr.decode("UTF-8"))
    return ret


def tpe_submit_commands(kwargs, mpileups, thread_count, logger, shell_var=True):
    """run commands on number of threads"""
    with ThreadPoolExecutor(max_workers=thread_count) as e:
        for p in mpileups:
            e.submit(
                partial(varscan2, kwargs, logger=logger, shell_var=shell_var),
                p,
            )


def varscan_process_somatic(dct, vcf, logger, shell_var=True):
    """run varscan2 process somatic and picard UpdateVcfSequenceDictionary"""
    vps_cmd = [
        "java",
        "-d64",
        "-XX:+UseSerialGC",
        "-Xmx3G",
        "-jar",
        "/opt/VarScan.v2.3.9.jar",
        "processSomatic",
        vcf,
        "--min-tumor-freq",
        str(dct["min_tumor_freq"]),
        "--maf-normal-freq",
        str(dct["max_normal_freq"]),
        "--p-value",
        str(dct["vps_p_value"]),
    ]
    logger.info("VarScan processSomatic Args: %s", " ".join(vps_cmd))
    vps_cmd_output = subprocess_commands_pipe(" ".join(vps_cmd), logger, shell_var=shell_var)
    if vps_cmd_output != 0:
        logger.error("Failed on VarScan processSomatic.")


def varscan2(dct, mpileup, logger, shell_var=True):
    """run varscan2 workflow"""
    output_base = os.path.basename(mpileup)
    vs_cmd = [
        "java",
        "-d64",
        "-XX:+UseSerialGC",
        "-Xmx" + str(dct["java_opts"]),
        "-jar",
        "/opt/VarScan.v2.3.9.jar",
        "somatic",
        mpileup,
        output_base,
        "--mpileup",
        "1",
        "--min-coverage",
        str(dct["min_coverage"]),
        "--min-coverage-normal",
        str(dct["min_coverage_normal"]),
        "--min-coverage-tumor",
        str(dct["min_coverage_tumor"]),
        "--min-var-freq",
        str(dct["min_var_freq"]),
        "--min-freq-for-hom",
        str(dct["min_freq_for_hom"]),
        "--normal-purity",
        str(dct["normal_purity"]),
        "--tumor-purity",
        str(dct["tumor_purity"]),
        "--p-value",
        str(dct["vs_p_value"]),
        "--somatic-p-value",
        str(dct["somatic_p_value"]),
        "--strand-filter",
        str(dct["strand_filter"]),
        "--output-vcf",
        str(dct["output_vcf"]),
    ]
    if dct["validation"]:
        vs_cmd += ["--validation"]
    logger.info("VarScan2 somatic Args: %s", " ".join(vs_cmd))
    vs_cmd_output = subprocess_commands_pipe(
        " ".join(vs_cmd), logger, shell_var=shell_var
    )
    if vs_cmd_output != 0:
        logger.error("Failed on VarScan2 somatic calling.")
    else:
        snp_vcf = output_base + ".snp.vcf"
        indel_vcf = output_base + ".indel.vcf"
        varscan_process_somatic(
            dct, snp_vcf, logger, shell_var=shell_var
        )
        varscan_process_somatic(
            dct, indel_vcf, logger, shell_var=shell_var
        )


def merge_outputs(output_list, merged_file):
    """Merge scattered outputs"""
    first = True
    with open(merged_file, "w") as oh:
        for out in output_list:
            with open(out) as fh:
                for line in fh:
                    if first or not line.startswith("#"):
                        oh.write(line)
            first = False
    return merged_file


def get_file_size(filename):
    """ Gets file size """
    fstats = os.stat(filename)
    return fstats.st_size


def get_args():
    """
    Loads the parser.
    """
    # Main parser
    parser = argparse.ArgumentParser("Internal multithreading Varscan2.3.9 pipeline.")
    # Required flags
    parser.add_argument(
        "-m",
        "--tn_pair_pileup",
        action="append",
        required=True,
        help="The mpileup files for tumor/normal pair."
    )
    parser.add_argument(
        "-d",
        "--ref_dict",
        required=True,
        help="reference sequence dictionary file."
    )
    parser.add_argument(
        "-c",
        "--thread_count",
        type=int,
        default=2,
        help="Number of thread."
    )
    parser.add_argument(
        "-j",
        "--java_opts",
        default="3G",
        help="JVM -Xmx argument."
    )
    parser.add_argument(
        "-mc",
        "--min_coverage",
        type=int,
        default=8,
        help="Minimum coverage in normal and tumor to call variant (8)"
    )
    parser.add_argument(
        "-mcn",
        "--min_coverage_normal",
        type=int,
        default=8,
        help="Minimum coverage in normal to call somatic (8)"
    )
    parser.add_argument(
        "-mct",
        "--min_coverage_tumor",
        type=int,
        default=6,
        help="Minimum coverage in tumor to call somatic (6)"
    )
    parser.add_argument(
        "-mvf",
        "--min_var_freq",
        type=float,
        default=0.10,
        help="Minimum variant frequency to call a heterozygote (0.10)"
    )
    parser.add_argument(
        "-mffh",
        "--min_freq_for_hom",
        type=float,
        default=0.75,
        help="Minimum frequency to call homozygote (0.75)"
    )
    parser.add_argument(
        "-np",
        "--normal_purity",
        type=float,
        default=1.00,
        help="Estimated purity (non-tumor content) of normal sample (1.00)"
    )
    parser.add_argument(
        "-tp",
        "--tumor_purity",
        type=float,
        default=1.00,
        help="Estimated purity (tumor content) of tumor sample (1.00)"
    )
    parser.add_argument(
        "-vspv",
        "--vs_p_value",
        type=float,
        default=0.99,
        help="P-value threshold to call a heterozygote (0.99)"
    )
    parser.add_argument(
        "-spv",
        "--somatic_p_value",
        type=float,
        default=0.05,
        help="P-value threshold to call a somatic site (0.05)"
    )
    parser.add_argument(
        "-sf",
        "--strand_filter",
        type=int,
        default=0,
        help="If set to 1, removes variants with >0.9 strand bias (0)"
    )
    parser.add_argument(
        "-v",
        "--validation",
        action="store_true",
        help="If set, outputs all compared positions even if non-variant"
    )
    parser.add_argument(
        "-ov",
        "--output_vcf",
        type=int,
        default=1,
        help="If set to 1, output VCF instead of VarScan native format"
    )
    parser.add_argument(
        "-mtf",
        "--min_tumor_freq",
        type=float,
        default=0.10,
        help="Minimun variant allele frequency in tumor [0.10]"
    )
    parser.add_argument(
        "-mnf",
        "--max_normal_freq",
        type=float,
        default=0.05,
        help="Maximum variant allele frequency in normal [0.05]"
    )
    parser.add_argument(
        "-vppv",
        "--vps_p_value",
        type=float,
        default=0.07,
        help="P-value for high-confidence calling [0.07]"
    )
    return parser.parse_args()


def main(args, logger):
    """main"""
    logger.info("Running VarScan v2.3.9")
    kwargs = vars(args)

    # Start Queue
    tpe_submit_commands(kwargs, kwargs["tn_pair_pileup"], kwargs["thread_count"], logger)

    # Check outputs
    snps = glob.glob("*snp.Somatic.hc.vcf")
    indels = glob.glob("*indel.Somatic.hc.vcf")
    assert len(snps) == len(indels) == len(kwargs["tn_pair_pileup"]), "Missing output!"
    if any(get_file_size(x) == 0 for x in snps + indels):
        logger.error("Empty output detected!")

    # Merge
    merged_snps = "multi_varscan2_snp_merged.vcf"
    merged_indels = "multi_varscan2_indel_merged.vcf"
    merge_outputs(snps, merged_snps)
    merge_outputs(indels, merged_indels)


if __name__ == "__main__":
    # CLI Entrypoint.
    start = time.time()
    logger_ = setup_logger()
    logger_.info("-" * 80)
    logger_.info("multi_varscan2_p3.py")
    logger_.info("Program Args: %s", " ".join(sys.argv))
    logger_.info("-" * 80)

    args_ = get_args()

    # Process
    logger_.info(
        "Processing tumor-normal mpileups: %s",
        ", ".join(args_.tn_pair_pileup)
    )
    main(args_, logger_)

    # Done
    logger_.info("Finished, took %s seconds", round(time.time() - start, 2))
