# basespace_import
Helper commands to import reads using basespace's CLI given the name of the sequencing run.

This is pretty specific to our use case, but should be easily adaptable.



*This assumes that the basespace CLI is installed, active, and connected with the correct data*



## downloadReads

Download all reads associated with a given run name or ID. 

Unless a run_id is specified (see getRunIDFromName), automatically tries to match the run name to an existing sequencing run

### Python

```
downloadReads(
	run_name, 
	run_dir, 
	run_id="", 
	verify_most_recent=True, 
	match_biosample_name=True, 
	underscore_to_dash=True
	)
```

### CLI

```
bs_import run_name run_dir
		--run_id=""
		--verify_most_recent=True
		--match_biosample_name=True
		--underscore_to_dash=True
```



## getRunInfo

Gets all BaseSpace info about a given run and saves this info to a path and/or prints to console.

Unless a run_id is specified (see getRunIDFromName), automatically tries to match the run name to an existing sequencing run

### Python

```
getRunInfo(
	run_name, 
	run_id="", 
	out_path="bs_info", 
	out_format='csv', 
	do_print=False
	)
```

### CLI

```
bs_run_info run_name 
		--run_id=""
		--out_path=bs_info
		--out_format=csv [csv, table, json, yaml, xml]
		--do_print=False
```



## getRunIDFromName

Returns the ID of a run whose ExperimentName or Name matches/contains given run_name

Exits and prints all names/IDs if multiple IDs match

### Python

```
getRunIDFromName(run_name, do_print=False)
```

### CLI

```
bs_run_id run_name
```

