# qb-monitor
A simple web app to monitor multiple qbittorrent instances

## Usage
1. Copy `conf.py.default` to `conf.py` and add your qb info there. (Edit to this file can take effect without restarting the service)
2. Start the web app

For development only:
```
flask --app main run --host=0.0.0.0 --port 5001 --reload
```
In production
```
gunicorn -w 4 'main:app' -b 127.0.0.1:5001
```
3. browser http://127.0.0.1:5001
4. Alternatively, put it behind a reverse proxy like NGINX and mount it under a subdirectory
```
location /qm/ {
    proxy_pass   http://127.0.0.1:5001/;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Prefix /qm;
}
```
