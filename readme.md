# Environment

This project is expected to run in the [Mininet-WiFi virtual machine](https://drive.google.com/file/d/1R8n4thPwV2krFa6WNP0Eh05ZHZEdhw4W/view?usp=sharing),
because we utilise WiFi simulation of it.

To get everything work as expected, please make sure your system is up to date by running the following commands:

```bash
sudo apt update
sudo apt upgrade
```

You will also need to install Ryu and sFlow-RT on the Mininet-WiFi VM, because we use Ryu as SDN controller.
Installation steps are shown below.


# Installing Ryu on Mininet-WiFi VM

To install Ryu on Mininet-WiFi VM:

```bash
# Seems Ryu only works with Python 3: 
# https://stackoverflow.com/questions/21170521/function-annotations-giving-error-in-python

# Better upgrade setuptools first. 
# I ran into some trouble and the struck through answer in the following link somehow helped me: 
# https://github.com/googleapis/google-cloud-python/issues/3757#issuecomment-321028963
sudo pip3 install --upgrade setuptools

# Install Ryu
pip3 install --user ryu

# Newest version of eventlet (updated several days ago) causes some error. Install an older version instead: 
# https://stackoverflow.com/questions/67409452/gunicorn-importerror-cannot-import-name-already-handled-from-eventlet-wsgi
pip3 install eventlet==0.30.2
```

Please refer to [pip installation guide](https://pip.pypa.io/en/stable/installing/) if `pip3` doesn't work on your VM.

# Installing sFlow-RT and mininet-dashboard

```
# Download and extract sFlow-RT
wget https://inmon.com/products/sFlow-RT/sflow-rt.tar.gz
tar -xvzf sflow-rt.tar.gz

# Insteall mininet-dashboard app for sFlow-RT
sflow-rt/get-app.sh sflow-rt mininet-dashboard

# Start sFlow-RT
./sflow-rt/start.sh

```

# Running the code

First, go to the project directory. The program needs to be run from the project directory to operate properly.

Next, to start the topology, issue command:

```bash
sudo python topo.py --remote
```

The `--remote` option instructs Mininet to use a remote controller on `127.0.0.1` port 6653 (default configuration). 
If you wish to run with Mininet's default controller, just rip off the `--remote` option.

Also, you'll need to run the controller program:

```bash
ryu-manager controller.py
```

