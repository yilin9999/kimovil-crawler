.PHONY: run
#include ./.env

# make headline colorful
TAG="\n\n\033[0;32m\#\#\# "
END=" \#\#\# \033[0m\n"

freeze-pkg:
	@echo $(TAG)Deploy$(END)	
	./venv/bin/pip freeze > requirements.txt			

venv:
	@echo $(TAG)Generate python 3 virtualenv$(END)
	virtualenv --python=python3.5 --no-site-packages venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install --upgrade setuptools
	venv/bin/pip install --upgrade wheel
	venv/bin/pip install -r requirements.txt

activate-venv:
	sh -c ' . ./venv/bin/activate'

update_url_run:
	rm -f kimovil_url.txt
	make run
	
run:
	sh -c ' . ./venv/bin/activate ; python3 kimovil_crawler.py'	
