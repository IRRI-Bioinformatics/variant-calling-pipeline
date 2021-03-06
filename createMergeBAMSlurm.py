#!/usr/bin/env python

import sys, re, os, os.path
from classes import CreateMergeBAMParams

# get the genome file
input_file = sys.argv[1]
disk = sys.argv[2]

# get the parameters in the class CreateMergeBAMParams
params = CreateMergeBAMParams()

# reads the config file and get the respective values for each
for line in open(params.fp):
    if re.findall(r'email=', line): params.email = line.split('=')[-1].rstrip()
    elif re.findall(r'sleep=', line): params.sleep = line.split('=')[-1].rstrip()
    elif re.findall(r'bamutil=', line): params.bamutil = line.split('=')[-1].rstrip()
    elif re.findall(r'samtool=', line): params.samtools = line.split('=')[-1].rstrip()
    elif re.findall(r'partition=', line): params.partition = line.split('=')[-1].rstrip()
    elif re.findall(r'cpu_mergebam=', line): params.cpu_mergebam = line.split('=')[-1].rstrip()
    elif re.findall(r'input_dir=', line): params.input_dir = line.split('=')[-1].rstrip()
    elif re.findall(r'output_dir=', line): params.output_dir = line.split('=')[-1].rstrip()
    elif re.findall(r'scripts_dir=', line): params.scripts_dir = line.split('=')[-1].rstrip()
    elif re.findall(r'analysis_dir=', line): params.analysis_dir = line.split('=')[-1].rstrip()
    elif re.findall(r'reference_dir=', line): params.reference_dir = line.split('=')[-1].rstrip()

# reads the file containing the genome
for line in open(input_file):
    line = line.split(":")
    genome = line[0]

    # directory where slurm script will store
    path = params.analysis_dir + "/" + disk
    slurm_file = "submit_mergebam_slurm.sh"
    exec_file = os.path.join(path, slurm_file)

    output_path = params.analysis_dir + "/" + disk + "/" + genome
    mergebam_file = genome + "-mergebam.slurm"
    output_file = os.path.join(output_path, mergebam_file)

    # creates a submit shell script between job submission
    # to prevent timeout
    script = open(exec_file, "w")
    script.write("#!/bin/bash\n")
    script.write("\n")
    script.write("sbatch " + output_file + "\n")
    script.write("sleep " + params.sleep + "\n")
    script.close()

    # creates slurm script
    mergebam = open(output_file, "w")
    mergebam.write("#!/bin/bash\n")
    mergebam.write("\n")

    mergebam.write("#SBATCH -J " + genome + "\n")
    mergebam.write("#SBATCH -o " + genome + "-mergebam.%j.out\n")
    mergebam.write("#SBATCH -c " + params.cpu_mergebam + "\n")
    mergebam.write("#SBATCH --partition=" + params.partition + "\n")
    mergebam.write("#SBATCH -e " + genome + "-mergebam.%j.error\n")
    mergebam.write("#SBATCH --mail-user=" + params.email + "\n")
    mergebam.write("#SBATCH --mail-type=begin\n")
    mergebam.write("#SBATCH --mail-type=end\n")
    mergebam.write("#SBATCH --requeue\n")
    mergebam.write("\n")

    # loads the module to be used
    mergebam.write("module load bamutil/" + params.bamutil + "\n")
    mergebam.write("module load samtools/" + params.samtools + "\n")
    # mergebam.write("module load python/" + params.python + "\n")
    mergebam.write("\n")

    # get the first pair of a fastq file and assign for use
    mergebam.write("python " + params.scripts_dir + "/mergebam.py -o " + params.output_dir + " -g " + genome + "\n")
    mergebam.write("python " + params.scripts_dir + "/bamvalidator.py -b " + params.output_dir + "/" + genome + "/ -o " + params.output_dir + "/" + genome + "\n")
    mergebam.write("mv " + genome + "-sam2bam.*.error " + genome + "-sam2bam.*.out " + params.analysis_dir + "/" + disk + "/" + genome + "/logs")
    mergebam.close()
