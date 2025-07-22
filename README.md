# Secure Snippets

Secure Snippet has been created so that someone can share private information with someone else in a relatively secure manner. The snippet's content is encrypted using a key which is not stored on the server's database but rather is transmitted to the user through the snippet URL constructed. Once the snippet is read by the destinator (or by any potential MITM), the snippet is destroyed in the server's database.

This allows the destinator of the message to know if he's the only one to read the message and if not, to contact the source to notify him that something went wrong.

## Technical description

### TL;DR

  1. User create a snippet by filling the form
  2. The API give the user a link he can send to the destination
  3. The destination browse that link and see the sensitive information
  4. That information is destroyed from the snippet's database

### Details

  * Snippets are encrypted using a 32 bytes random string and stored in MongoDB;
  * That secret key is never stored on the server but is sent once to the creator of the snippet;
  * If the creator has ticked the unformatted content option, display will be wrapped around pre tags
  * if the creator has ticked the "send confirmation" option:
    - Creator also need to fill email and reference
    - When the destinator reads the snippet, he will receive an email along with the reference
    - Both email and reference will also be encrypted in the server's database, so privacy is ensured
  * If the admin calls the clean API function, snippets older than a certain amount of days are removed;

## API

### Add a snippet

  * Method: POST
  * Call: /api/snippet
  * Arguments:
    - content: snippet content
    - isRaw: unformatted content (1 or 0)
    - isConfirm: we want a confirmation (1 or 0)
    - isFile: file upload (1 or 0)
    - reference: reference of the source regarding the snippet
    - email: Email on where to send confirmation
  * Content-type: application/json
  * Returns:
    - id: the ID of the snippet
    - key: encryption key used for this snippet
    - msg: success or failure message
    - rc: return code (0 == success)

### Read a snippet

  * Method: GET
  * Call: /api/snippet/*id*/*key*
  * Content-type: application/json
  * Returns:
    - content
    - created: unix timestamp
    - id: id of the snippet
    - isRaw

### Clean old snippets

  * Method: GET
  * Call: /api/clean/*secret*
  * Content-type: application/json
  * Returns:
    - rc
    - count


## Configuration

### Virtualenv setup

```
$ git clone ...
$ cd snippet
$ virtualenv .
$ source bin/activate
$ pip install -r requirements.txt
```

### Apache virtualhost

```
<IfModule mod_ssl.c>
<VirtualHost *:443>
        ServerAdmin thomas@espix.net
        ServerName  snippet.espix.net

        ErrorLog ${APACHE_LOG_DIR}/snippet-ssl-error.log
        CustomLog ${APACHE_LOG_DIR}/snippet-ssl_access.log combined

        SSLEngine on
        SSLCertificateFile    /etc/letsencrypt/live/snippet.espix.net/fullchain.pem
        SSLCertificateKeyFile  /etc/letsencrypt/live/snippet.espix.net/privkey.pem

        WSGIDaemonProcess snippet user=snippet group=snippet threads=5 python-path=/srv/snippet/app/lib/python3.5/site-packages
        WSGIScriptAlias /api /srv/snippet/app/snippet.wsgi/api
        WSGIScriptReloading on

        <Directory /srv/snippet/app>
                WSGIProcessGroup snippet
                #WSGIPassAuthorization On
                WSGIApplicationGroup %{GLOBAL}
                Require all granted
        </Directory>

        DocumentRoot /srv/snippet/app/static
        <Directory />
                Options None
                AllowOverride None
        </Directory>

        <Directory /srv/snippet/app/static/>
                Options None
                AllowOverride All
                Require all granted
        </Directory>

        # avoid clickjacking
        Header always append X-Frame-Options DENY

</VirtualHost>
</IfModule>
```
