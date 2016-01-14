import os
import subprocess

def get_pileup(ref, bam, out, logger=None):
    """ create the pileup using samtools"""

    if not(os.path.isfile(ref) and os.path.isfile(bam)):
        raise Exception("Reference file %s or BAM file %s not found. Please check the file exists and the path is correct" %(ref, bam))
    if not os.path.abspath(out):
        raise Exception("Path to directory %s to which the output must be written  not found." %(os.path.abspath(out)))

    cmd = ["time", "samtools", "mpileup", "-f", ref, bam]

    with open(out, "w") as outfile:
        child = subprocess.Popen(cmd, stdout=outfile, stderr=subprocess.PIPE)
        stdout, stderr = child.communicate()
        exit_code = child.returncode

    outfile.close()

    if logger != None:
        stderr = stderr.split("\n")
        for line in stderr:
            logger.info(line)

    return exit_code

def run_varscan(normal, tumor, outbase, args, varscan_path="/home/ubuntu/bin", logger=None):
    """ run varscan on normal and tumor pileups """

    cmd = ["time", "java", "-jar", varscan_path, "somatic", normal, tumor, outbase,
            "--output-snp", args.output_snp,
            "--output-indel", args.output_indel,
            "--min-coverage", args.min_coverage,
            "--min-coverage-normal", args.min_coverage_normal,
            "--min-coverage-tumor", args.min_coverage_tumor,
            "--min-var-freq", args.min_var_freq,
            "--min-freq-for-hom", args.min_freq_for_hom,
            "--normal-purity", args.normal_purity,
            "--tumor-purity", args.tumor_purity,
            "--p-value", args.p-value,
            "--somatic-p-value", args.somatic_p_value,
            "--strand-filter", args.strand_filter,
            "--validation", args.validation,
            "--output-vcf", args.output_vcf
            ]

    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
    stdout, stderr = child.communicate()
    exit_code = child.returncode

    if logger != None:
        stderr = stderr.split("\n")
        for line in stderr:
            logger.info(line)

    return exit_code
