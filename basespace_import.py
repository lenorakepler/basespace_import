import sys
import subprocess
import datetime
import click
from pathlib import Path
import pandas as pd

def getRunIDFromName(run_name):
	"""
	Returns the ID of a run whose ExperimentName or Name matches/contains given run_name
	Exits and prints all names/IDs if multiple IDs match
	"""
	run_id = subprocess.run(f"bs list runs -F ExperimentName -F Name -F Id -f csv | grep '{run_name}' | cut -d, -f3",
			shell=True, capture_output=True, text=True).stdout.splitlines()

	if len(run_id) == 1:
		return run_id[0]

	elif len(run_id) == 0:
		sys.exit(f"No runs match '{run_name}'")

	else:
		matching = subprocess.run(f"bs list runs -F ExperimentName -F Name -F Id -f csv | grep '{run_name}'", shell=True, capture_output=True, text=True).stdout
		sys.exit(f"Multiple runs match '{run_name}':\n{matching}")

def getRunInfo(run_name, run_id="", out_path=f"bs_info", out_format='csv', do_print=False):
	"""
	Get all BaseSpace info about a given run
	Saves to a path and/or prints to console
	"""

	# If no run ID specified, grab it from the table by name
	if not run_id:
		run_id = getRunIDFromName(run_name)
	
	out_file = Path(out_path).with_suffix(f".{out_format}")
	out_file.parent.mkdir(exist_ok=True, parents=True)

	out_str = subprocess.run(f"bs get run -i '{run_id}' -f {out_format}", shell=True, capture_output=True, text=True).stdout

	if out_str:
		if out_path:
			out_file.write_text(out_str)

		if do_print:
			sys.stdout.write(out_str)

	else:
		sys.exit(f"Issue getting info for '{run_name}' with id {run_id}")

@click.command()
@click.argument('run_name')
@click.option('--run_id', default="")
@click.option('--out_path', default=f"bs_info")
@click.option('--out_format', default='csv', type=click.Choice(['csv', 'table', 'json', 'yaml', 'xml'], case_sensitive=False))
@click.option('--do_print', default=False)
def bs_run_info(run_name, run_id, out_path, do_print, out_format):
	getRunInfo(
		run_name=run_name, 
		run_id=run_id, 
		out_path=out_path, 
		out_format=out_format,
		do_print=do_print
		)

@click.command()
@click.argument('run_name')
@click.option('--do_print', default=False)
def bs_run_id(run_name, do_print):
	run_id = getRunIDFromName(run_name)
	if do_print:
		sys.stdout.write(f"Run ID for {run_name}: {run_id}")

def downloadReads(run_name, run_dir, run_id="", verify_most_recent=True, match_biosample_name=True, underscore_to_dash=True):
	"""
	Downloads all .fastq reads from the specified run to a folder named "reads" inside the specified directory
	"""

	run_reads = run_dir / "reads"
	run_reads.mkdir(exist_ok=True, parents=True)

	# If no run ID specified, grab it from the table by name
	if not run_id:
		run_id = getRunIDFromName(run_name)

	if verify_most_recent:
		# Get table of .fastq datasets
		sys.stdout.write(f"Getting table of .fastq datasets associated with {run_name} (ID: {run_id})")
		subprocess.run(f"bs list datasets --input-run {run_id} --is-type illumina.fastq.v1.8 -F Id -F Name -F TotalSize -F DateModified -F AppSession.Name -F AppSession.Application.Id -F AppSession.QcStatus -f csv > {run_dir}/{run_name}_fastq_sets.csv", shell=True)
		fastq_sets = pd.read_csv(f"{run_dir}/{run_name}_fastq_sets.csv", index_col="Id")
		
		# Find most recent .fastq file versions
		# Output a csv listing these to downlaod
		recent = []
		for n, ndf in fastq_sets.groupby('Name'):
			ndf.sort_values(by=['DateModified'], inplace=True, ascending=False)
			recent.append(ndf.iloc[0, :].copy())

		to_dl = pd.concat(recent, axis=1).T
		to_dl.to_csv(f"{run_dir}/{run_name}_fastqs_to_download.csv")

		# Download most recent .fastq files
		for id, row in to_dl.iterrows():
			# Get biosample name
			biosample_name = row['Name'].split('_L0')[0]
			
			if underscore_to_dash:
				biosample_name = biosample_name.replace("_", "-")

			# Download the files associated with a dataset
			subprocess.run(f'bs download dataset -i {id} -o {run_reads}', shell=True)

			if match_biosample_name:
				# If "Name" doesn't match filename of fastq file, rename fastq file after download
				# Get filenames of downloaded files (in case they do not match the sample name)
				file_names_io = subprocess.run(f"bs dataset content -i {id} -F FilePath -f csv", shell=True, stdout=subprocess.PIPE, text=True)
				file_names = file_names_io.stdout.splitlines()
				
				# If downloaded files don't have correct sample name (doesn't match biosample), rename
				for file_name in file_names:
					fastq_sample_name = file_name.split('_S')[0]
					if fastq_sample_name != biosample_name:
						new_file_name = file_name.replace(fastq_sample_name, biosample_name)
						(run_reads / file_name).rename(run_reads / new_file_name)
						sys.stdout.write(f"Renamed to match biosample name: {file_name} --> {new_file_name}")
	
	else:
		# Download all .fastq data associated with the run
		subprocess.run(
			f'bs list datasets --input-run {run_id} --is-type illumina.fastq.v1.8 --terse |  xargs -n1 -I@ bs download dataset -i @ -o {run_reads}',
			shell=True
			)

		# If converting all underscores to dashes
		if underscore_to_dash:
			for file in run_reads.glob("*.fastq.gz"):
				new_name = file.name.split('_S')[0].replace("_", "-")
				(run_reads / file.name).rename(run_reads / new_name)
				sys.stdout.write(f"Renamed to convert underscores: {file.name} --> {new_name}")

@click.command()
@click.argument('run_name')
@click.option('--run_id', default="")
def main(run_name, run_id, out_dir):
	run_dir = locs.all_runs / run_name
	run_dir.mkdir(exist_ok=True, parents=True)
	getRunInfo(run_name, out_path=run_dir / "bs_info", run_id=run_id)
	downloadReads(run_name, run_dir, run_id)

if __name__ == "__main__":
	main()
