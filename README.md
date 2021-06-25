# HydraulicPandanusCrest

Docker, nginx, uwsgi, flask, celery (with gevent) and redis stack for managing patching and inventory json records on about 250 linux servers, vms and workstations

## Docker containers

Orchestrated with docker-compose

- nginx - reverse proxy the uwsgi server from 8080 to host port 80
- flask - slim buster python 3.8/9 for flask website, api, HPCtools,
- worker - slim buster python 3.8/9 for celery workers
- redis - messaage broker backend for celery tasks

In the HPC environment background scripts (not in this repo yet) run to check host machines for patches pending, hardware physical or virtual etc.
Each host has an inventory file with it's known config (hardware / virtualisation, network, mem, cpu, role, contact /owner) **docroot**/inventory/config/**hostname**.json
The regular (nightly) scripts check for patches pending, uptime etc and report back to a cache
**docroot**/patching/config/**hostname**.json

Celery and Billiard pool (rather than multiprocessing )(or eventlet gevent depending upon the day of the week at the moment) split reading as parsing of a glob  *.json in folder into a Pandas dataframe and hot link each host to the equivalent inventory/host.json file rendered as a web table. Hosts sorted by days since last scanned (nightly if up) then days waiting on patching and highlighted Amber at 50 days, Red at 60, (also on uptime)If hosts havent been seen in a scan for over a day they will be at the bottom of the list, going cold purple if they have been down over a week.
rendering of current jobs on grid queue (Univa sge like in my case, but could be SLURM whatever)
