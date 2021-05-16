# Environment

This project is expected to run in the [Mininet-WiFi virtual machine](https://drive.google.com/file/d/1R8n4thPwV2krFa6WNP0Eh05ZHZEdhw4W/view?usp=sharing),
because we utilise WiFi simulation of it.

You will also need to install Ryu on the Mininet-WiFi VM, because we use Ryu as SDN controller.
Installation steps are shown below.


# Installing Ryu on Mininet-WiFi VM

To install Ryu on Mininet-WiFi VM:

```bash
# Seems Ryu only works with Python 3: 
# https://stackoverflow.com/questions/21170521/function-annotations-giving-error-in-python
# Re-install Pip for Python 3.5
curl https://bootstrap.pypa.io/pip/3.5/get-pip.py -o get-pip.py
sudo python3 get-pip.py

# Need to upgrade setuptools. The struck through answer somehow helped me: 
# https://github.com/googleapis/google-cloud-python/issues/3757#issuecomment-321028963
sudo pip3 install --upgrade setuptools

# Install Ryu
pip3 install --user ryu

# Newest version of eventlet (freshly several days ago) causes some error. Install an older version instead: 
# https://stackoverflow.com/questions/67409452/gunicorn-importerror-cannot-import-name-already-handled-from-eventlet-wsgi
pip3 install eventlet==0.30.2
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

