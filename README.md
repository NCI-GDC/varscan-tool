# GDC VarScan2
![Version badge](https://img.shields.io/badge/VarScan-v2.3.9-<COLOR>.svg)

VarScan is a platform-independent mutation caller for targeted, exome, and whole-genome resequencing data generated on Illumina, SOLiD, Life/PGM, Roche/454, and similar instruments. The VarScan2 can be used to detect different types of variation:
*   Germline variants (SNPs an dindels) in individual samples or pools of samples.
*   Multi-sample variants (shared or private) in multi-sample datasets (with mpileup).
*   Somatic mutations, LOH events, and germline variants in tumor-normal pairs.
*   Somatic copy number alterations (CNAs) in tumor-normal exome data.


Original VarScan2: http://dkoboldt.github.io/varscan/

## Docker

There are two `Dockerfile`s for different purposes:

* Vanilla VarScan2
  * `/docker/Dockerfile` : VarScan2 docker without additional features.
* Multi-threading VarScan2
  * `/docker/multi_varscan2/Dockerfile` : A python multi-threading implementation on VarScan2 with builtin `processSomatic` filtering. To achieve `scatter/gather` method on Docker level, input needs an array of tumor-normal mpileup from `samtools mpileup -f`.

## How to build

https://docs.docker.com/engine/reference/builder/

The docker images are tested under multiple environments. The most tested ones are:
* Docker version 19.03.2, build 6a30dfc
* Docker version 18.09.1, build 4c52b90
* Docker version 18.03.0-ce, build 0520e24
* Docker version 17.12.1-ce, build 7390fc6

## For external users
The repository has only been tested on GDC data and in the particular environment GDC is running in. Some of the reference data required for the workflow production are hosted in [GDC reference files](https://gdc.cancer.gov/about-data/data-harmonization-and-generation/gdc-reference-files "GDC reference files"). For any questions related to GDC data, please contact the GDC Help Desk at support@nci-gdc.datacommons.io.

There is a production-ready CWL example at https://github.com/NCI-GDC/varscan-cwl which uses the docker images that are built from the `Dockerfile`s in this repo.

To use docker images directly or with other workflow languages, we recommend to build and use either vanilla VarScan2 or multi-threading VarScan2.

To run multi-threading VarScan2:

```
[INFO] [20200114 21:50:13] [multi_varscan2] - --------------------------------------------------------------------------------
[INFO] [20200114 21:50:13] [multi_varscan2] - multi_varscan2_p3.py
[INFO] [20200114 21:50:13] [multi_varscan2] - Program Args: docker/multi_varscan2/multi_varscan2_p3.py -h
[INFO] [20200114 21:50:13] [multi_varscan2] - --------------------------------------------------------------------------------
usage: Internal multithreading Varscan2.3.9 pipeline. [-h] -m TN_PAIR_PILEUP
                                                      -d REF_DICT
                                                      [-c THREAD_COUNT]
                                                      [-j JAVA_OPTS]
                                                      [-mc MIN_COVERAGE]
                                                      [-mcn MIN_COVERAGE_NORMAL]
                                                      [-mct MIN_COVERAGE_TUMOR]
                                                      [-mvf MIN_VAR_FREQ]
                                                      [-mffh MIN_FREQ_FOR_HOM]
                                                      [-np NORMAL_PURITY]
                                                      [-tp TUMOR_PURITY]
                                                      [-vspv VS_P_VALUE]
                                                      [-spv SOMATIC_P_VALUE]
                                                      [-sf STRAND_FILTER] [-v]
                                                      [-ov OUTPUT_VCF]
                                                      [-mtf MIN_TUMOR_FREQ]
                                                      [-mnf MAX_NORMAL_FREQ]
                                                      [-vppv VPS_P_VALUE]

optional arguments:
  -h, --help            show this help message and exit
  -m TN_PAIR_PILEUP, --tn_pair_pileup TN_PAIR_PILEUP
                        The mpileup files for tumor/normal pair.
  -d REF_DICT, --ref_dict REF_DICT
                        reference sequence dictionary file.
  -c THREAD_COUNT, --thread_count THREAD_COUNT
                        Number of thread.
  -j JAVA_OPTS, --java_opts JAVA_OPTS
                        JVM -Xmx argument.
  -mc MIN_COVERAGE, --min_coverage MIN_COVERAGE
                        Minimum coverage in normal and tumor to call variant
                        (8)
  -mcn MIN_COVERAGE_NORMAL, --min_coverage_normal MIN_COVERAGE_NORMAL
                        Minimum coverage in normal to call somatic (8)
  -mct MIN_COVERAGE_TUMOR, --min_coverage_tumor MIN_COVERAGE_TUMOR
                        Minimum coverage in tumor to call somatic (6)
  -mvf MIN_VAR_FREQ, --min_var_freq MIN_VAR_FREQ
                        Minimum variant frequency to call a heterozygote
                        (0.10)
  -mffh MIN_FREQ_FOR_HOM, --min_freq_for_hom MIN_FREQ_FOR_HOM
                        Minimum frequency to call homozygote (0.75)
  -np NORMAL_PURITY, --normal_purity NORMAL_PURITY
                        Estimated purity (non-tumor content) of normal sample
                        (1.00)
  -tp TUMOR_PURITY, --tumor_purity TUMOR_PURITY
                        Estimated purity (tumor content) of tumor sample
                        (1.00)
  -vspv VS_P_VALUE, --vs_p_value VS_P_VALUE
                        P-value threshold to call a heterozygote (0.99)
  -spv SOMATIC_P_VALUE, --somatic_p_value SOMATIC_P_VALUE
                        P-value threshold to call a somatic site (0.05)
  -sf STRAND_FILTER, --strand_filter STRAND_FILTER
                        If set to 1, removes variants with >0.9 strand bias
                        (0)
  -v, --validation      If set, outputs all compared positions even if non-
                        variant
  -ov OUTPUT_VCF, --output_vcf OUTPUT_VCF
                        If set to 1, output VCF instead of VarScan native
                        format
  -mtf MIN_TUMOR_FREQ, --min_tumor_freq MIN_TUMOR_FREQ
                        Minimun variant allele frequency in tumor [0.10]
  -mnf MAX_NORMAL_FREQ, --max_normal_freq MAX_NORMAL_FREQ
                        Maximum variant allele frequency in normal [0.05]
  -vppv VPS_P_VALUE, --vps_p_value VPS_P_VALUE
                        P-value for high-confidence calling [0.07]
```

## For GDC users

See https://github.com/NCI-GDC/gdc-somatic-variant-calling-workflow.
