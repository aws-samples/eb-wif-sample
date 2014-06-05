import json
import os, binascii
from flask import Flask, render_template, request, url_for, redirect, session

# Flask Initialization
# global variable must be named "application" as per EB requirement
application = Flask(__name__)
application.debug = True

# secret key to encode session cookie (http://flask.pocoo.org/docs/quickstart/#sessions)
application.secret_key = binascii.b2a_hex(os.urandom(30))

#
# Read config file and create Identity provider
#
def getIdentityProvider(provider) :
    import os
    from IdentityProvider import getIdentityProvider
    

    
    appID      = os.environ.get(provider.upper() + '_APP_ID')
    appSecret  = os.environ.get(provider.upper() + '_APP_SECRET')
    roleARN    = os.environ.get(provider.upper() + '_ROLE_ARN')
    
    return getIdentityProvider(provider, appID, appSecret, roleARN)
    
@application.route("/")
def index():
    enabled_providers = getEnabledProviders()
    return render_template('default.html', enabled_providers=enabled_providers)
    
@application.route("/privacy")
def privacy():
    return render_template('privacy.html')

@application.route('/initiateLogin/<provider>')
def initiateLogin(provider):
    print '--- Initiate login for provider : ' + provider
    return redirect(getIdentityProvider(provider).loginURL())

@application.route('/oauth2callback/<provider>')
def OAuth2Callback(provider):
    print '--- OAuth2Callback called for IP : ' + provider  
    
    code  = request.args.get('code', 'unknown') 
    if (code == 'unknown'):
        result = render_template('error.html')
    else:
        credentials, profile = getIdentityProvider(provider).oauthCallback(code)
        
        import urllib
        # _scheme is required for SSL, see
        # https://github.com/mitsuhiko/flask/issues/773
        #url = url_for('s3', _scheme="https", _external=True, **dict(credentials.items() + profile.items()))
        url = url_for('s3', _scheme="https", _external=True)
        #print '--- redirect url : ' + url

        # save credentials and profile in the server side session
        session.update(credentials)
        session.update(profile)
        #print '--- session : ' + str(session)

        result = redirect(url)
            
    return result
    
@application.route('/s3/')
def s3():
    # all args are provided in the session

    # workaround URL encoding issue where + signs are replaced by ' '
    # it looks like it is a bug introduced with Flask 0.10.1 (0.9 is OK)
    # https://github.com/mitsuhiko/flask/issues/771
    session['session_token'] = session['session_token'].replace(' ', '+')
    session['access_key'] = session['access_key'].replace(' ', '+')
    session['secret_key'] = session['secret_key'].replace(' ', '+')
    
    # call S3 to list buckets
    buckets = doListBuckets(session)
    
    return render_template('s3.html', buckets=buckets, args=session)
    
def getEnabledProviders():
  providers = ['amazon', 'facebook', 'google']
  enabled = []
  
  for provider in providers:
    if os.environ.get(provider.upper() + '_APP_ID') and os.environ.get(provider.upper() + '_APP_SECRET') and os.environ.get(provider.upper() + '_ROLE_ARN'):
      enabled.append(provider)
  
  return enabled
    
def doListBuckets(credentials):
    from boto.s3.connection import S3Connection
        
    conn = S3Connection(credentials['access_key'], credentials['secret_key'], security_token=credentials['session_token'])
    buckets = conn.get_all_buckets()
    return [bucket.name for bucket in buckets]

if (__name__ == "__main__"):
    application.run(debug=True)

