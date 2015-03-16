Whisper
-----------------
[![Build Status](https://travis-ci.org/NoiSek/whisper.svg)](https://travis-ci.org/NoiSek/whisper)
[![Coverage Status](https://coveralls.io/repos/NoiSek/whisper/badge.svg)](https://coveralls.io/r/NoiSek/whisper)

Anonymous, encrypted email.

Todo:
 - Implement private key encryption
 - Rewrite example Nginx config in https for various webservers
 - Add ability for original authors to view and optionally delete messages using cookies or sessions.
 - Add optional time expiration
 - Implement docker for painless installation
 - Expand test coverage, break unit testing into more modular pieces

###Installing Whisper
Whisper is a Python 3 application.

To begin the installation process, install the Python Development Headers and Python 3. On Ubuntu this would be:
```
  sudo apt-get install python3.4 python3.4-dev openssl
``

To install all the necessary Python requirements, navigate to the root directory and use:

```
  sudo pip install -r requirements.txt
```

####Requirements

#####System Dependencies
 - Python 3.4+
 - Python3.4+ Development Headers
 - OpenSSL

#####Python Dependencies
 - Gunicorn
 - Bottle
 - Bottle-sqlite
 - Requests
 - pyOpenSSL

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
Make sure the user you're running Whisper as has write permissions to the current directory, then run 'gunicorn app' from your root Whisper directory to start.

Whisper config will be automatically generated in your root folder if it isn't already present, the config follows this structure:

```
  {
    "api_key": "",
    "domain": "yourdomain.com",
    "salt": ""
  }
```

Note that if a salt is not provided then it will automatically be generated.
To acquire an API key (10,000 free emails a month) head here: http://mailgun.com
