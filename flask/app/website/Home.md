# HPC Admin Dashboard

## Features and status of HPC website

Dashboard status of on prem vm cluster, and compute grid
*TODO: Add AWS view of EC2 instances via AWS cli*

- Website Home page is rendered from markdown file
- Patching list (uptime and days pending patching)generated dynamically from mounted hostname.json files
  - Hostname page summarising patches needed and inventory data for host hot-linked from patching hostname
  - Working notes for host linked and rendered from hostname.md markdown
  - Patching scatter & Distro graph generated when patching list is parsed
- Inventory list generated dynamically from mounted inventory.json
- Grid status (subprocess call to sge command)
- Listener for webhooks (mail-out or action completed git pipelines)
- Generate timeline or 'landscape' (vm lifecycle or projects etc.)from uploaded CSV file
  - Uploader [link](./timeline_upload), Display last chart [link](./timeline)
- *TODO: Add container with lmutilities to show products with floating licenses in use*
- *TODO: Incorporate license log visualisations mail-out monthly report via celerybeat*
- *TODO: Some sort of traffic light with availability Time since last ping etc.*

- API: /api/ root loads README.md as html with and API usage details
  - API section was developed to deliver RESTful services
  - /api/inventory JSON view of all inventory files for upload to CMDB
  - *TODO: any field mapping required of CMDB (configuration management DB)*
