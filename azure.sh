#!/bin/bash


/var/docker/atp/restoreunstable
cd /home/rianad/test_graphics
mv /home/rianad/test_graphics/azure-override/docker-compose.override.yml /var/docker/atp
cd /var/docker/atp ; docker-compose up -d