# Flask application in production using Apache

Using **WSGI (Web Server Gateway Interface)**. 
by using **mod_wsgi** (WSGI compliant interface as Apache module). 

### Step 1: Install Necessary Packages

1. **Install Apache** if it's not already installed on your server:

```bash
sudo apt update
sudo apt install apache2
```

* Windows

* [Download](https://www.apachelounge.com/download/VS17/binaries/httpd-2.4.62-240904-win64-VS17.zip)

Set env variable `C:\httpd\bin`

Install service

```bash
httpd -k install
Apache2.4 start
```

2. **Install `mod_wsgi`** to interface Apache with Python:

```bash
sudo apt install libapache2-mod-wsgi-py3
```

This installs the WSGI module for Python 3.

3. **Install Flask** and any other Python dependencies you need:

```bash
pip install flask
```

### Step 2: Set Up the Flask Application

Assume your Flask application is in a file called `app.py` and it has a typical structure like this:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run()
```

You'll want to modify your `app.py` to avoid calling `app.run()` in production (as that's mainly for development). For production, you don't need to run the app manually; Apache will serve it via WSGI.

Rename the entry point of your app to something like `app = Flask(__name__)` (as shown above). It will later be referenced by Apache.

### Step 3: Create a WSGI File

Next, create a `.wsgi` file, which is used by Apache to interface with your Flask app. This file typically resides in the same directory as your Flask app or in `/var/www/`.

For example, create a file called `myapp.wsgi`:

```bash
nano /var/www/myapp/myapp.wsgi
```

Contents of the `myapp.wsgi` file:

```python
import sys
import os

# Add your project directory to the sys.path
sys.path.insert(0, '/var/www/myapp')

# Activate the virtual environment if needed (optional)
# activate_this = '/path/to/venv/bin/activate_this.py'
# exec(open(activate_this).read(), {'__file__': activate_this})

# Import the application (Flask instance)
from app import app as application
```

### Step 4: Configure Apache

Now you need to configure Apache to serve your Flask app using `mod_wsgi`.

1. **Create a new Apache configuration file**:

   ```bash
   sudo nano /etc/apache2/sites-available/myapp.conf
   ```

   Contents of the file:

   ```apache
   <VirtualHost *:80>
       ServerName myapp.com
       ServerAdmin webmaster@myapp.com

       WSGIDaemonProcess myapp user=www-data group=www-data threads=5
       WSGIScriptAlias / /var/www/myapp/myapp.wsgi

       <Directory /var/www/myapp>
           Require all granted
       </Directory>

       Alias /static /var/www/myapp/static
       <Directory /var/www/myapp/static/>
           Require all granted
       </Directory>

       ErrorLog ${APACHE_LOG_DIR}/myapp_error.log
       CustomLog ${APACHE_LOG_DIR}/myapp_access.log combined
   </VirtualHost>
   ```

   - `ServerName`: Replace this with your domain or IP address.
   - `WSGIScriptAlias`: This points to the `.wsgi` file created earlier.
   - `/var/www/myapp`: Path to your Flask app.

2. **Enable the site** and `mod_wsgi`:

   ```bash
   sudo a2ensite myapp
   sudo a2enmod wsgi
   ```

3. **Restart Apache**:

   ```bash
   sudo systemctl restart apache2
   ```

### Step 5: Set Up Permissions

Ensure that the directory `/var/www/myapp` and its contents are readable by Apache. You can do this by changing the ownership to `www-data` (the Apache user):

```bash
sudo chown -R www-data:www-data /var/www/myapp
```

### Step 6: (Optional) Virtual Environment

If you're using a virtual environment, you'll need to modify the `.wsgi` file to activate it. To do this:

1. **Activate the virtual environment in the `.wsgi` file** by adding the following code:

   ```python
   activate_this = '/var/www/myapp/venv/bin/activate_this.py'
   exec(open(activate_this).read(), {'__file__': activate_this})
   ```

   Make sure to replace `/var/www/myapp/venv/` with the path to your virtual environment.

### Step 7: Test the Setup

Now, visit your server’s IP address or domain. If everything is set up correctly, you should see your Flask app running.

---

### Summary

To deploy a Flask web application in production using Apache:

1. Install Apache and `mod_wsgi`.
2. Prepare a `.wsgi` file to point Apache to your Flask app.
3. Create a virtual host configuration for Apache.
4. Set up necessary permissions and restart Apache.

This is the idiomatic way to run a Flask application with Apache in a production environment.