# qb-monitor
A simple web app to monitor multiple qbittorrent instances

## Usage
1. Copy `config.json.default` to `config.json` and add your qb info there. (Edit to this file can take effect without restarting the service)
2. Start the web app

```
python main.py
```
3. browser http://127.0.0.1:5001
4. Alternatively, put it behind a reverse proxy like NGINX and mount it under a subdirectory
```
location /qm/ {
    proxy_pass   http://127.0.0.1:5001/;
    proxy_set_header X-Forwarded-Prefix /qm;
}
```
