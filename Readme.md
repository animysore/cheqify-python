# Cheqify

### Instructions to run locally for development

Run with Flask's Server

    python3 flaskserver.py 

Run with Gunicorn

    gunicorn --bind 0.0.0.0:8000 flaskserver:app

### Updating Code on Server after running

1. SSH into the VM instance on GCP

2. Navigate to the folder on the VM

        cd /home/aniruddha_mysore/cheqify-server

3. Pull the latest changes

        git pull

4. Restart Gunicorn service

        sudo systemctl restart gunicorn

5. Restart Nginx (not really needed)

    sudo systemctl restart nginx

6. Clear downloaded data from api (Optional)

To clear the data already downloaded from the API, run `clearcache.sh` script located in the `server` folder. 

    ./clearcache.sh

### Reading Error logs

1. Error logs of gunicorn 

        systemctl status gunicorn

2. Error logs of nginx

        tail -f /var/log/nginx/error.log

### How to setup server from scratch (if needed) ( instructions for latest versions of Linux which use `systemd` )

0. Get yer Linux shell matey.

1. Install all dependencies

    Python:

    1. gunicorn  
    
            pip3 install gunicorn
            
    2. Will list rest later, for now just run `python3 flaskserver.py` and install anything that's missing.

    Linux:

    1. git: 
    
           sudo apt-get install git
    
    2. nginx: 
    
            sudo apt-get install nginx

2. Clone the repository from github

        git clone https://github.com/AniMysore74/cheqify-python.git

3. Navigate into the cloned directory

        cd cheqify-python

4. Setup gunicorn as a system service

To create a new service, we place a `<my_fav_service>.service` file in the `/etc/systemd/system/` directory. A sample of what the file should look like is already included in this repository, in `server/gunicron.service`

The file looks like this: 

```

[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=aniruddha_mysore
Group=www-data
WorkingDirectory=/home/aniruddha_mysore/cheqify-python/server
ExecStart=/usr/local/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/aniruddha_mysore/cheqify-python/server/cheqify.sock flaskserver:app

[Install]
WantedBy=multi-user.target

```

Edit this file to suit your configurations:

    1. Change User to your user
    
    2. Change WorkingDirectory to the location of the server/ folder inside the cloned folder

    3. Change the directory location as needed inside the ExecStart command


After making changes, this file needs to be added to `/etc/systemd/system/`. Just copy the file into the required directory with a GUI, or 

    `sudo cp gunicorn.service /etc/systemd/system` 

Note that we bind gunicorn to a Unix web socket, instead of using a static IP address.

Now, start your gunicorn service by running

    `sudo systemctl start gunicorn`

To see if the service is running successfully 

    `systemctl status gunicorn`

If the service is running correctly, you should see a `cheqify.sock` file in your `server` folder. (Assuming the given configurations)

5. Configure nginx

Nginx needs to be configured to proxy requests from port 80 (the default port browsers) to the web socket that gunicorn runs on. A sample configuration file can be found in `server/nginx-conf`

```
server {
    listen 80;
    server_name 35.200.185.242;
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/aniruddha_mysore/cheqify-python/server/;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/aniruddha_mysore/cheqify-python/server/cheqify.sock;
    }
}

```

Edit this configuration file and change the directory location as needed. We also configure nginx to directly serve requets using `/static/` in the path name from our `server/static` folder. This means static file requests need not be passed to the app server.

The `server_name` should hold either the global IP of your server or the domain name

After configuration, copy the contents of this file into a new file `cheqify` in the `/etc/nginx/sites-available/` folder. 

    sudo cp nginx-conf /etc/nginx/sites-available/cheqify 

Then create a link of the new file in `/etc/nginx/sites-enabled`

    sudo ln -s /etc/nginx/sites-available/cheqify /etc/nginx/sites-enabled/cheqify

And your nginx configuration is done. Start nginx by running 

    sudo systemctl start nginx

Now go to the IP address specified in `server_name` and you should see your beautiful flask app deployed successfully!