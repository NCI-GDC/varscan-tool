import os
import subprocess
import pipelineUtil

def get_pileup(ref, bam, out, logger=None):
    """ create the pileup using samtools"""

    if not(os.path.isfile(ref) and os.path.isfile(bam)):
        raise Exception("Reference file %s or BAM file %s not found. Please check the file exists and the path is correct" %(ref, bam))
    if not os.path.abspath(out):
        raise Exception("Path to directory %s to which the output must be written  not found." %(os.path.abspath(out)))

    logger.info("Sarting mpileup for %s" %bam)
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

def run_varscan(normal, tumor, outbase, args, logger=None):
    """ run varscan on normal and tumor pileups """

    cmd = ["time", "java", "-jar", args.varscan_path, "somatic", normal, tumor, outbase,
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
            "--validation", args.validation,
            "--output-vcf", args.output_vcf
            ]

    #the SNP and indel files are generated as per the base name.
    #if different values are provided, then they are added to the call.

    if not (args.output_snp == "output.snp"):
        cmd = cmd + ["--output-snp" , args.output_snp]

    if not (args.output_indel == "output.indel"):
        cmd = cmd + ["--output-indel", args.output_indel]

    logger.info("Starting Varscan Somatic Calls")

    exit_code = pipelineUtil.run_command(cmd, logger)

    return exit_code

def varscan_high_confidence(args, snp, logger=None):
    """ get high-confidence SNPs """

    cmd = ["time", "java", "-jar", args.varscan_path, "processSomatic", snp,
            "--min-tumor-freq", args.min_tumor_freq,
            "--max-normal-freq", args.max_normal_freq,
            "--p-value", args.p_high_confidence,
            ]

    logger.info("Starting Varscan processSomatic")

    exit_code = pipelineUtil.run_command(cmd, logger)

    return exit_code
