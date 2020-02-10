install:
	cp -r $(PWD) /usr/local/var
	crontab /usr/local/var/academic-twitter-csv/scripts/crontab
