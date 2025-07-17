run:
	python iphone_backup.py

install:
	pip install -e .

pyenv:
	pyenv virtualenv 3.11.4 iphone-image-backup
	pyenv local iphone-image-backup
