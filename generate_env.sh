#!/usr/bin/bash
printf "\n# Settings/base.py\n\n" > .env
grep "env(" -r readthedocs/settings/base.py  | cut -d'(' -f2 | sed 's/"//g' | sed 's/,/=/' | sed "s/)//" | cut -d',' -f1 | sed "s/^/#/" >> .env
printf "\n# Settings/docker_compose.py\n\n" >> .env
grep "env(" -r readthedocs/settings/docker_compose.py  | cut -d'(' -f2 | sed 's/"//g' | sed 's/,/=/' | sed "s/)//" | cut -d',' -f1 | sed "s/^/#/">> .env


