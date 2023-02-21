# qb-monitor
A simple web app to monitor multiple qbittorrent instances

## Usage
1. Copy `conf.py.default` to `conf.py` and add your qb info there
2. Start the web app
For development only
```
flask --app main run --host=0.0.0.0 --port 5001 --reload
```
3. browser http://127.0.0.1:5001
