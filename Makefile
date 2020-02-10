install:
	cp ./scripts/download.py /usr/local/bin/academic-twitter-scraper.py
	cp -r $(PWD) /usr/local/var
	crontab /usr/local/var/academic-twitter-csv/scripts/crontab

clean:
	rm /usr/local/bin/academic-twitter-scraper.py
	rm -rf /usr/local/var/academic-twitter-csv
	rm *.csv
