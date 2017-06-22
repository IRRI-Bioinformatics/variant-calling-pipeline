#!/usr/bin/env python

import sys, re, os
import os.path
from classes import CreateVariantCallingParams
from classes import writeFile

file = sys.argv[1]
disk = sys.argv[2]

params = CreateVariantCallingParams()
attributes = [attr for attr in dir(params) if not callable(getattr(params, attr)) and not attr.startswith("__")]

for line in open(params.fp):
	for index, items in enumerate(attributes):
		if re.search(items, line):
			if re.findall(r'analysis_dir', line):
				params.analysis_dir = line.split('=')[-1].rstrip()

			elif re.findall(r'input_dir', line):
				params.input_dir = line.split('=')[-1].rstrip()

			elif re.findall(r'reference_dir', line):
				params.reference_dir = line.split('=')[-1].rstrip()

			elif re.findall(r'scripts_dir', line):
				params.scripts_dir = line.split('=')[-1].rstrip()

			elif re.findall(r'output_dir', line):
				params.output_dir = line.split('=')[-1].rstrip()

			elif re.findall(r'software_dir', line):
				params.software_dir = line.split('=')[-1].rstrip()

			elif re.findall(r'tmp_dir', line):
				params.tmp_dir = line.split('=')[-1].rstrip()

			elif re.findall(r'gatk', line):
				params.gatk = line.split('=')[-1].rstrip()

			elif re.findall(r'bgzip', line):
				params.bgzip = line.split('=')[-1].rstrip()

			elif re.findall(r'tabix', line):
				params.tabix = line.split('=')[-1].rstrip()

			elif re.findall(r'email', line):
				params.email = line.split('=')[-1].rstrip()

			elif re.findall(r'partition', line):
				params.partition = line.split('=')[-1].rstrip()

for line in open(file):
	line = line.split(":")
	genome = line[0]
	
	path = params.analysis_dir + "/" + disk
	genomeFile = "submit_bam2vcf_slurm.sh"

	script = open(os.path.join(path, genomeFile), "w")
	writeFile(script)
	script.close()

	path = params.analysis_dir + "/" + disk + "/" + genome
	genomeFile = genome + "-bam2vcf.sh"

	slurm = open(os.path.join(path, genomeFile), "w")
	slurm.write("#!/bin/bash\n")
	slurm.write("\n")

	slurm.write("#SBATCH -J " + genome + "-bam2vcf\n")
	slurm.write("#SBATCH -o " + genome + "-bam2vcf.%j.out\n")
	slurm.write("#SBATCH --cpus-per-task=8\n")
	slurm.write("#SBATCH --partition=$partition\n")
	slurm.write("#SBATCH -e " + genome + "-bam2vcf.%j.error\n")
	slurm.write("#SBATCH --mail-user=$email\n")
	slurm.write("#SBATCH --mail-type=ALL\n")
	slurm.write("#SBATCH --requeue\n")
	slurm.write("\n")

	slurm.write("module load python/2.7.11\n")
	slurm.write("module load jdk\n")
	slurm.write("module load samtools/1.0-intel\n")
	slurm.write("module load htslib/1.0-intel\n")
	slurm.write("\n")

	slurm.write("python " + params.scripts_dir + "/bam2vcf.py -b " + params.output_dir + genome + genome + ".merged.bam -r " + params.reference_dir + "r -g " + params.gatk + " -t " + params.tmp_dir + " -z " + params.bgzip + " -x " + params.tabix + "\n")
	slurm.write("mv " + genome + "-mergebam.*.error " + genome + "-mergebam.*.out " + genome + "-bam2vcf.*.error " + genome + "-bam2vcf.*.out " + params.analysis_dir + "/" + disk + "/" + genome + "/logs")
	slurm.close()