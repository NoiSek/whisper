# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 8080, host: 8080

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update

    # Install Python and dependencies
    sudo apt-get install -y python3.4 python3-pip libffi-dev
    sudo easy_install3 -U pip # Necessary due to an issue with the python-requests library
    sudo pip3 install -r /vagrant/requirements.txt
    sudo pip3 install coveralls

    # Install sass
    sudo apt-get install -y ruby
    sudo gem install sass

    # Install babel (does not use package.json)
    sudo apt-get install -y npm
    npm install -g babel
  SHELL
end