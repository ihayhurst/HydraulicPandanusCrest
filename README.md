# HydraulicPandanusCrest

Docker nginx/flask/uwsgi/celery/redis stack for managing patching and inventory json records on about 250 linux servers, vms and workstations

## Docker containers

Orchestrated with docker-compose

- nginx - reverse proxy the uwsgi server from 8080 to host port 80
- flask - slim buster python 3.8/9 for flask website, api, HPCtools,
- worker - slim buster python 3.8/9 for celery workers
- redis - messaage broker backend for celery tasks
- flower - monitor celery jobs

In the HPC environment background scripts run to check host machines patches pending, hardware physical or virtual etc. They generate and store centraly  a /patching/hostname.json
all known machines have an /inventory/hostname.json with what when where who type info

Celery and Billiard pool (rather than multiprocessing ) split reading as parsing of a glob  *.json in folder into a Pandas dataframe and hot link each host to the equivalent inventory/host.json file rendered as a web table. Hosts sorted by days since last scanned (nightly if up) then days waiting on patching and highlighted Amber at 50 days, Red at 60, (also on uptime)If hosts havent been seen in a scan for over a day they will be at the bottom of the list, going cold purple if they have been down over a week.
rendering of current jobs on grid queue (Univa sge like in my case, but could be SLURM whatever)
