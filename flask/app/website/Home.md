# Content included from Home.md

## Features and status of HPC website

Dashboard status of on prem vm cluster, and compute grid
*TODO: Add AWS view of EC2 instances via AWS cli*

- Website Home page is rendered from markdown file
- Patching list (uptime and days pending patching)generated dynamicaly from mounted hostname.json files
    - Hostname page sumarising patches needed and inventory data for host hotlinked from patching hostname
    - Working notes for host linked and rendered from hostname.md markdown
    - Patching scatter & Distro graph generated when patching likst is parsed
- Inventory list gerated dynamicaly from mounted inventory.json
- Grid status (subprocess call to sge command)
- Listner for webhooks (mailout or action completed git pipelines)
- Generate timeline or 'landscape' (vm lifecycle or projects etc.)from uploaded CSV file
    - Uploader [link](./timeline_upload), Display last chart [link](./timeline)
- *TODO: add container with lmutilities to show products with floating licenses in use*
- *TODO: incorporate license log visualisations mailout monthly report via celerybeat*

- API: /api/ root loads README.md as html with and API useage details
    - API section was developed to deliver RESTful view af Oracle database, code remains to implement a later API calls to databases if required
    - *TODO: include REST view of inventory files with fields mapped to rormat suitable to upload to CMDB (configuration management DB)*
