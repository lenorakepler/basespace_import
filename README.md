# basespace_import
Helper commands to import reads using basespace's CLI given the name of the sequencing run
This is pretty specific to our use case, but should be easily adaptable.



This assumes that the basespace CLI is installed, active, and connected with the correct data



Downloading reads can be done on the command line or in a python call



## downloadReads



## getRunInfo

Gets all BaseSpace info about a given run and saves this info to a path and/or prints to console

Unless a run_id is specified, automatically tries to match the run name to an existing sequencing run

### Python



### CLI

```
bs_run_info run_name 
		--run_id=""
		--out_path=bs_info
		--out_format=csv [csv, table, json, yaml, xml]
		--do_print=False
```

