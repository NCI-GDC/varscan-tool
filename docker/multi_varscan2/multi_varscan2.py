#!/usr/bin/env python
'''Internal multithreading Varscan2.3.9 pipeline'''

import glob
import os
import argparse
import subprocess
from multiprocessing import Pool
from functools import partial

def is_nat(x):
    '''Checks that a value is a natural number.'''
    if int(x) > 0:
        return int(x)
    raise argparse.ArgumentTypeError('%s must be positive, non-zero' % x)

def get_region(mpileup):
    '''ger region from mpileup filename'''
    namebase = os.path.basename(mpileup)
    base, ext = os.path.splitext(namebase)
    region = base.replace('-', ':', 1)
    return region, base

def run_command(cmd, shell_var=False):
    '''Runs a subprocess'''
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell_var)
    stdoutdata, stderrdata = child.communicate()
    exit_code = child.returncode
    print stdoutdata
    print stderrdata
    return exit_code

def varscan_process_somatic(vcf, mtf, mnf, vppv, rd):
    '''run varscan2 process somatic and picard UpdateVcfSequenceDictionary'''
    fileregion, fileroot = get_region(vcf)
    vps_cmd = [
        'java', '-d64', '-XX:+UseSerialGC',
        '-Xmx3G', '-jar', '/bin/VarScan.v2.3.9.jar',
        'processSomatic', vcf,
        '--min-tumor-freq', mtf,
        '--maf-normal-freq', mnf,
        '--p-value', vppv
    ]
    print('Processing somatic {} ...'.format(vps_cmd))
    vps_cmd_output = run_command(vps_cmd)
    if vps_cmd_output != 0:
        print('Failed on processing somatic.')
    else:
        hc_vcf = fileroot + '.Somatic.hc.vcf'
        filtered_vcf = RemoveNonStandardVariants(hc_vcf, fileroot + '.Somatic.hc.standard.vcf')
        output_file = fileroot + '.varscan2.somatic.hc.updated.vcf'
        pud_cmd = [
            'java', '-d64', '-XX:+UseSerialGC',
            '-Xmx3G', '-jar', '/usr/local/bin/picard.jar',
            'UpdateVcfSequenceDictionary', 'INPUT=' + filtered_vcf,
            'OUTPUT=' + output_file, 'SEQUENCE_DICTIONARY=' + rd
        ]
        print('Updating vcf seq dict {} ...'.format(pud_cmd))
        run_command(pud_cmd)

def varscan2(jo, rd, mc, mcn, mct, mvf, mffh, np, tp, vspv, spv, sf, val, ov, mtf, mnf, vppv, mpileup):
    '''run varscan2 workflow'''
    region, output_base = get_region(mpileup)
    vs_cmd = [
        'java', '-d64', '-XX:+UseSerialGC',
        '-Xmx' + jo, '-jar', '/bin/VarScan.v2.3.9.jar',
        'somatic', mpileup, output_base, '--mpileup', '1',
        '--min-coverage', mc,
        '--min-coverage-normal', mcn,
        '--min-coverage-tumor', mct,
        '--min-var-freq', mvf,
        '--min-freq-for-hom', mffh,
        '--normal-purity', np,
        '--tumor-purity', tp,
        '--p-value', vspv,
        '--somatic-p-value', spv,
        '--strand-filter', sf,
        '--output-vcf', ov
    ]
    if val: vs_cmd += ['--validation']
    print('Processing varscan2 somatic {} ...'.format(vs_cmd))
    vs_cmd_output = run_command(vs_cmd)
    if vs_cmd_output != 0:
        print('Failed on VarScan2 somatic calling.')
    else:
        snp_vcf = output_base + '.snp.vcf'
        indel_vcf = output_base + '.indel.vcf'
        varscan_process_somatic(snp_vcf, mtf, mnf, vppv, rd)
        varscan_process_somatic(indel_vcf, mtf, mnf, vppv, rd)

def RemoveNonStandardVariants(input, output):
    with open(output, 'w') as oh:
        with open(input, 'r') as fh:
            for line in fh:
                if line.startswith('#'):
                    check = False
                else:
                    good = set(['A', 'C', 'T', 'G'])
                    cols = line.rstrip('\r\n').split('\t')
                    alleles = cols[3].split(',') + cols[4].split(',')
                    alleles_set = set(list(''.join(alleles).upper()))
                    check = alleles_set - good
                if check:
                    continue
                else:
                    oh.write(line)
    return output

def merge_outputs(output_list, merged_file):
    first = True
    with open(merged_file, 'w') as oh:
        for out in output_list:
            with open(out) as fh:
                for line in fh:
                    if first or not line.startswith('#'):
                        oh.write(line)
            first = False
    return merged_file

def main():
    '''main'''
    parser = argparse.ArgumentParser('Internal multithreading Varscan2.3.9 pipeline.')
    # Required flags.
    parser.add_argument('-c', '--thread_count', type=is_nat, required=True, help='Number of thread.')
    parser.add_argument('-j', '--java_opts', required=True)
    parser.add_argument('-m', '--tn_pair_pileup', action="append", required=True, help='mpileup files.')
    parser.add_argument('-d', '--ref_dict', required=True, help='reference sequence dictionary file.')
    parser.add_argument('-mc', '--min_coverage', required=True)
    parser.add_argument('-mcn', '--min_coverage_normal', required=True)
    parser.add_argument('-mct', '--min_coverage_tumor', required=True)
    parser.add_argument('-mvf', '--min_var_freq', required=True)
    parser.add_argument('-mffh', '--min_freq_for_hom', required=True)
    parser.add_argument('-np', '--normal_purity', required=True)
    parser.add_argument('-tp', '--tumor_purity', required=True)
    parser.add_argument('-vspv', '--vs_p_value', required=True)
    parser.add_argument('-spv', '--somatic_p_value', required=True)
    parser.add_argument('-sf', '--strand_filter', required=True)
    parser.add_argument('-v', '--validation', action="store_true")
    parser.add_argument('-ov', '--output_vcf', required=True)
    parser.add_argument('-mtf', '--min_tumor_freq', required=True)
    parser.add_argument('-mnf', '--maf_normal_freq', required=True)
    parser.add_argument('-vppv', '--vps_p_value', required=True)
    args = parser.parse_args()
    mpileup = args.tn_pair_pileup
    threads = args.thread_count
    jo = args.java_opts
    rd = args.ref_dict
    mc = args.min_coverage
    mcn = args.min_coverage_normal
    mct = args.min_coverage_tumor
    mvf = args.min_var_freq
    mffh = args.min_freq_for_hom
    np = args.normal_purity
    tp = args.tumor_purity
    vspv = args.vs_p_value
    spv = args.somatic_p_value
    sf = args.strand_filter
    val = args.validation
    ov = args.output_vcf
    mtf = args.min_tumor_freq
    mnf = args.maf_normal_freq
    vppv = args.vps_p_value
    pool = Pool(int(threads))
    pool.map(partial(varscan2, jo, rd, mc, mcn, mct, mvf, mffh, np, tp, vspv, spv, sf, val, ov, mtf, mnf, vppv), mpileup)
    snp_outputs = glob.glob('*snp.varscan2.somatic.hc.updated.vcf')
    indel_outputs = glob.glob('*indel.varscan2.somatic.hc.updated.vcf')
    merge_outputs(snp_outputs, 'multi_varscan2_snp_merged.vcf')
    merge_outputs(indel_outputs, 'multi_varscan2_indel_merged.vcf')

if __name__ == '__main__':
    main()
