Whisper
-----------------
[![Build Status](https://travis-ci.org/NoiSek/whisper.svg)](https://travis-ci.org/NoiSek/whisper)
[![Coverage Status](https://coveralls.io/repos/NoiSek/whisper/badge.svg)](https://coveralls.io/r/NoiSek/whisper)

Anonymous, encrypted email.

Todo:
 - Rewrite example Nginx config in https for various webservers
 - Add ability for original authors to view and optionally delete messages using cookies or sessions.
 - Add optional time expiration
 - Implement docker for painless installation
 - Expand test coverage, break unit testing into more modular pieces
 - Queueing system when encrypting messages rather than competing for available memory

###Installing Whisper
Whisper is a Python 3 application. In development environments, skip all of the below and use [Vagrant](http://www.vagrantup.com/downloads) and run ```vagrant up``` instead.

To begin the installation process, install Python 3 and the Python development headers. On Ubuntu:

```
  sudo apt-get install python3.4 python3.4-dev libffi-dev
```

To install all the necessary Python requirements, navigate to the root directory and use:

```
  sudo pip install -r requirements.txt
```

####Requirements

#####System Dependencies
 - Python 3.4+
 - libffi-dev

#####Python Dependencies
 - Gunicorn
 - Bottle
 - Bottle-sqlite
 - Requests
 - pyNaCL

####Example Nginx config

```
  server {
    listen 80;
    server_name www.whisper.email;
    rewrite ^ https://whisper.email$request_uri? permanent;
  }

  server {
    listen 80;
    server_name whisper.email;
    root /var/www/whisper.email;

    location / {
      proxy_pass http://localhost:8080;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
      try_files $uri $uri/ =404;
    }
  }
```

###Setting up Whisper
Make sure the user you're running Whisper as has write permissions to the current directory, then run ```gunicorn app'``` from your root Whisper directory to start.

Whisper config will be automatically generated in your root folder if it isn't already present. The config follows this structure:

```
  {
    "api_key": "",
    "domain": "yourdomain.com",
    "salt": "",
    "private_key": "" # base64 encoded NaCl key
  }
```

Note that if a salt is not provided then it will automatically be generated.
To acquire an API key (10,000 free emails a month) head here: http://mailgun.com
