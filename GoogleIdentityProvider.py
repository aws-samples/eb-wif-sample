import json
from IdentityProvider import IdentityProvider 
from flask import request

class GoogleIdentityProvider(IdentityProvider):
        
    def getIDToken(self, token):
        return token['id_token']
    
    def loginURL(self):
        loginURL = 'https://accounts.google.com/o/oauth2/auth?response_type=code&'
        loginURL = loginURL + 'client_id=' + self.APP_ID + '&'
        loginURL = loginURL + 'redirect_uri=https%3A%2F%2F' + request.headers['Host']  + '%2Foauth2callback%2Fgoogle&'
        loginURL = loginURL + 'scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile'
        loginURL = loginURL + '&state=%2Fprofile'
        return loginURL
        
    def doGetToken(self,code):
        import httplib, urllib
    
        host = 'accounts.google.com'
        path = '/o/oauth2/token'
    
        data = 'code=' + code 
        data = data + '&client_id=' + self.APP_ID
        data = data + '&client_secret=' + self.APP_SECRET
        data = data + '&redirect_uri=https%3A%2F%2F' + request.headers['Host'] + '%2Foauth2callback%2Fgoogle'
        data = data + '&grant_type=authorization_code'

        headers = {'Content-type': 'application/x-www-form-urlencoded'} 
    
        conn = httplib.HTTPSConnection(host)
        conn.request('POST', path, data, headers)
        resp = conn.getresponse()
        return json.loads(resp.read())
        
    def doGetUserProfile(self,token):
        import urllib2, json
        response = urllib2.urlopen('https://www.googleapis.com/oauth2/v1/userinfo?access_token=' + token)
        googleProfile = json.loads(response.read())
        return { 'name' : googleProfile['name'], 'firstname' : googleProfile['given_name'],
                 'email' : googleProfile['email'], 'picture' : googleProfile['picture'],
                 'provider' : 'Google'}
    
    def getRoleARN(self):
        return self.ROLE_ARN        
