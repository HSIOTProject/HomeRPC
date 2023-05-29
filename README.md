This repo requires pye3dc.

local.py shows how to connect to an E3DC system on the local network.
web.py shows how to connect to an E3DC system via the internet using the web portal.

Run for testing:
```gunicorn main:app --reload```

Note:
The library `charset-normalizer` is for some reason not intalled with Pipenv on ReaspberryPi ubuntu so it had to be manually added here. It is required to run gunicorn or uvicorn.


Deploy:
- `pipenv install`
- Put this `@reboot cd /home/ubuntu/E3DC && /home/ubuntu/.local/bin/pipenv run gunicorn main:app -b 127.0.0.1:9000 > /home/ubuntu/e3dc.log 2>&1` into crontab
