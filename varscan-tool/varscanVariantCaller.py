import os
import subprocess
from cdis_pipe_utils import time_util
from cdis_pipe_utils import pipe_util

def get_pileup(ref, nbam, tbam, out, args, logger=None):
    """ create the pileup using samtools"""

    if not os.path.isfile(ref):
        raise Exception("Reference file %s not found. Please check the file exists and the path is correct" %ref)
    if not os.path.isfile(nbam):
        raise Exception("Normal bam file %s not found. Please check the file exists and the path is correct" %nbam)
    if not os.path.isfile(tbam):
        raise Exception("Tumor bam file %s not found. Please check the file exists and the path is correct" %tbam)
    if not os.path.abspath(out):
        raise Exception("Path to directory %s to which the output must be written  not found." %(os.path.abspath(out)))
    if not (int(args.q) >= 0):
        raise Exception("Quality filter cannot be negative")

    logger.info("Sarting mpileup for %s and %s" %(nbam, tbam))

    cmd = "samtools mpileup -f %s -q %s" %(ref, args.q)

    if int(args.b):
        cmd += " -B"

    if int(args.ff):
        cmd += " --ff %s" %args.ff

    cmd += " %s %s > %s" %(nbam, tbam, out)

    print cmd
    output = pipe_util.do_shell_command(cmd, logger)
    metrics = time_util.parse_time(output)

    return metrics


def run_varscan(pileup, outbase, args, logger=None):
    """ run varscan on normal and tumor pileups """

    cmd = ["time", "java", "-jar", args.varscan_path, "somatic", pileup, outbase,
            "--mpileup", "1",
            "--min-coverage", args.min_coverage,
            "--min-coverage-normal", args.min_coverage_normal,
            "--min-coverage-tumor", args.min_coverage_tumor,
            "--min-var-freq", args.min_var_freq,
            "--min-freq-for-hom", args.min_freq_for_hom,
            "--normal-purity", args.normal_purity,
            "--tumor-purity", args.tumor_purity,
            "--p-value", args.p_value,
            "--somatic-p-value", args.somatic_p_value,
            "--strand-filter", args.strand_filter,
            ]

    #Set output validation and format

    if int(args.validation):
        cmd = cmd + ['--validation']

    if int(args.output_vcf):
        cmd = cmd + ['--output-vcf']

    #the SNP and indel files are generated as per the base name.
    #if different values are provided, then they are added to the call.

    if not (args.output_snp == "output.snp"):
        cmd = cmd + ["--output-snp" , args.output_snp]

    if not (args.output_indel == "output.indel"):
        cmd = cmd + ["--output-indel", args.output_indel]


    logger.info("Starting Varscan Somatic Calls")

    output = pipe_util.do_command(cmd, logger)
    metrics = time_util.parse_time(output)

    return metrics

def varscan_high_confidence(args, snp, logger=None):
    """ get high-confidence SNPs """

    cmd = ["time", "java", "-jar", args.varscan_path, "processSomatic", snp,
            "--min-tumor-freq", args.min_tumor_freq,
            "--max-normal-freq", args.max_normal_freq,
            "--p-value", args.p_high_confidence,
            ]

    logger.info("Starting Varscan processSomatic")

    output = pipe_util.do_command(cmd, logger)
    metrics = time_util.parse_time(output)

    return metrics
