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