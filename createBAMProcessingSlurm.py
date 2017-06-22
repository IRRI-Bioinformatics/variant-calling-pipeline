#!/usr/bin/env python

import sys, re, os
import os.path
from classes import CreateBAMProcessingParams
from classes import writeFile

file = sys.argv[1]
disk = sys.argv[2]

params = CreateBAMProcessingParams()
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

			elif re.findall(r'picard', line):
				params.picard = line.split('=')[-1].rstrip()

			elif re.findall(r'email', line):
				params.email = line.split('=')[-1].rstrip()

			elif re.findall(r'partition', line):
				params.partition = line.split('=')[-1].rstrip()

for line in open(file):
	line = line.split(":")
	genome = line[0]
	count = int(line[1]) / 2

	os.makedirs(params.analysis_dir + "/" + disk + "/" + genome + "/logs")
	
	path = params.analysis_dir + "/" + disk
	genomeFile = "submit_sam2bam_slurm.sh"

	script = open(os.path.join(path, genomeFile), "w")
	writeFile(script)
	script.close()

	path = params.analysis_dir + "/" + disk + "/" + genome
	genomeFile = genome + "-sam2bam.sh"

	slurm = open(os.path.join(path, genomeFile), "w")
	slurm.write("#!/bin/bash\n")
	slurm.write("\n")

	slurm.write("#SBATCH -J " + genome + "\n")
	slurm.write("#SBATCH -o " + genome + "-sam2bam.%j.out\n")
	slurm.write("#SBATCH --cpus-per-task=6\n")
	slurm.write("#SBATCH --array=1-" + str(count) + "\n")
	slurm.write("#SBATCH --partition=$partition\n")
	slurm.write("#SBATCH -e -" + genome + "sam2bam.%j.error\n")
	slurm.write("#SBATCH --mail-user=$email\n")
	slurm.write("#SBATCH --mail-type=begin\n")
	slurm.write("#SBATCH --mail-type=end\n")
	slurm.write("#SBATCH --requeue\n")
	slurm.write("\n")

	slurm.write("module load python\n")
	slurm.write("module load jdk\n")
	slurm.write("filename=`find " + params.output_dir + "/" + genome + " -name \"*.sam\" | tail -n +\${SLURM_ARRAY_TASK_ID} | head -1`\n")
	slurm.write("\n")

	slurm.write("python " + params.scripts_dir + "/sam2bam.py -s \$filename -r " + params.reference_dir + " -p $picard -g $gatk -j $jvm -t $tmp_dir\n")
	slurm.write("mv " + genome + "-fq2sam.*.error " + genome + "-fq2sam.*.out " + params.analysis_dir + "/" + disk + "/" + genome + "/logs")
	slurm.close()