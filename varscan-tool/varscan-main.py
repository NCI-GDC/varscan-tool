import setupLog
import pipelineUtil
import os
import logging
import argparse
import varscanVariantCaller
import multiprocessing

if __name__=="__main__":

    parser = argparse.ArgumentParser(description="Variant calling using Varscan")
    required = parser.add_argument_group("Required input parameters")
    required.add_argument("--ref", default=None, help="path to reference genome", required=True)
    required.add_argument("--normal", default=None, help="path to normal bam file", required=True)
    required.add_argument("--tumor", default=None, help="path to tumor bam file", required=True)
    required.add_argument("--outdir", default=None, help="path to output directory", required=True)


    optional = parser.add_argument_group("optional input parameters")
    optional.add_argument("--uuid", default="unknown", help="unique identifier")
    optional.add_argument("--varscan_path", default="/home/ubuntu/bin/VarScan.jar", help="path to varscan jar")

    somatic = parser.add_argument_group("VarScan somatic input parameters")
    somatic.add_argument("--output_snp", default="output.snp", help="Output file for SNP calls")
    somatic.add_argument("--output_indel", default="output.indel", help="Output file for indel calls")
    somatic.add_argument("--min_coverage", default="8", help="Minimum coverage in normal and tumor to call variant")
    somatic.add_argument("--min_coverage_normal", default="8", help="Minimum coverage in normal to call somatic")
    somatic.add_argument("--min_coverage_tumor", default="6", help="Minimum coverage in tumor to call somatic")
    somatic.add_argument("--min_var_freq", default="6", help="Minimum variant frequency to call a heterozygote")
    somatic.add_argument("--min_freq_for_hom", default="0.75", help="Minimum frequency to call homozygote")
    somatic.add_argument("--normal_purity", default="1.0", help="Estimated purity (non-tumor content) of normal sample")
    somatic.add_argument("--tumor_purity", default="1.00", help="Estimated purity (tumor content) of tumor sample")
    somatic.add_argument("--p_value", default="0.99", help="P-value threshold to call a heterozygote")
    somatic.add_argument("--somatic_p_value", default="0.05", help="P-value threshold to call a somatic site")
    somatic.add_argument("--strand_filter", default="0", help="If set to 1, removes variants with >90% strand bias")
    somatic.add_argument("--validation", default="0", help="If set to 1, outputs all compared positions even if non-variant")
    somatic.add_argument("--output_vcf", default="0", help="If set to 1, output VCF instead of VarScan native format")

    processSomatic = parser.add_argument_group(" VarScan processSomatic input parameters")
    processSomatic.add_argument("--min_tumor_freq", default="0.10", help="Minimum variant allele frequency in tumor")
    processSomatic.add_argument("--max_normal_freq", default="0.05", help="Maximum variant allele frequency in normal")
    processSomatic.add_argument("--p_high_confidence", default="0.07", help="P-value for high-confidence calling")

    args = parser.parse_args()

    if not os.path.isfile(args.ref):
        raise Exception("Could not find reference file %s, please check that the file exists and the path is correct" %args.ref)

    if not os.path.isfile(args.normal):
        raise Exception("Could not find bam file %s, please check that the file exists and the path is correct" %args.normal)

    if not os.path.isfile(args.tumor):
        raise Exception("Could not find bam file %s, please check that the file exists and the path is correct" %args.tumor)

    if not os.path.isdir(args.outdir):
        os.mkdirs(args.outdir)

    log_file = "%s.varscan.log" %(os.path.join(args.outdir, args.uuid))
    logger = setupLog.setup_logging(logging.INFO, args.uuid, log_file)


    normal_pileup = os.path.join(args.outdir, "%s.normal.pileup" %args.uuid)
    tumor_pileup = os.path.join(args.outdir, "%s.tumor.pileup" %args.uuid)

    """
    pool = multiprocessing.Pool(processes=2)
    results = list()

    bams = ["normal", "tumor"]
    for i in xrange(len(bams)):

        if bams[i] == "normal":
            input_bam = args.normal
            pileup = os.path.join(args.outdir, "%s.normal.pileup" %args.uuid)
            log = setupLog.setup_logging(logging.INFO, "normal", "%s.mpileup.normal.log" %(os.path.join(args.outdir, args.uuid)))

        elif bams[i] == "tumor":
            input_bam = args.tumor
            pileup = os.path.join(args.outdir, "%s.tumor.pileup" %args.uuid)
            log = setupLog.setup_logging(logging.INFO, "tumor", "%s.mpileup.tumor.log" %(os.path.join(args.outdir, args.uuid)))

        rvalue = pool.apply_async(varscanVariantCaller.get_pileup, (args.ref, input_bam, pileup, log))
        results.append(rvalue)

    for rvalue in results:
        exit_code = rvalue.get()
        if exit_code != 0:
            raise Exception("Cannot run VarScan because pileup exited with a non-zero exitcode")

    #norm_exit_code = pool.apply_async(varscanVariantCaller.get_pileup, (args.ref, args.normal, normal_pileup, logger))
    #tumor_exit_code = pool.apply_async(varscanVariantCaller.get_pileup, (args.ref, args.tumor, tumor_pileup, logger))
    """
    norm_exit_code = varscanVariantCaller.get_pileup(args.ref, args.normal, normal_pileup, logger)
    tumor_exit_code = varscanVariantCaller.get_pileup(args.ref, args.tumor, tumor_pileup, logger)

    if not(norm_exit_code and tumor_exit_code):

        base = os.path.join(args.outdir, args.uuid)
        somatic_exit_code = varscanVariantCaller.run_varscan(normal_pileup, tumor_pileup, base, args, logger)
        if not somatic_exit_code:

            snp = "%s.snp" %base
            if args.output_vcf == "1":
                snp = "%s.vcf" %snp

            if os.path.isfile(snp):
                processSomatic_exit_code = varscanVariantCaller.varscan_high_confidence(args, snp, logger)

                if processSomatic_exit_code:
                    logger.error("VarScan processSomatic exited with non-zero exit code %s" %processSomatic_exit_code)

            else:
                raise Exception("Could not find output %s from VarScan" %snp)
        else:
            logger.error("VarScan somatic exited with a non-zero exit code %s" %somatic_exit_code)
    else:
        logger.error("Samtools pileup for tumor and normal exited with following exit-codes: normal %s and tumor %s" %(norm_exit_code, tumor_exit_code))


