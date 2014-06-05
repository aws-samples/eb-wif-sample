import json
from IdentityProvider import IdentityProvider 
from flask import request

class AmazonIdentityProvider(IdentityProvider):  
    
    def loginURL(self):
        loginURL = 'https://www.amazon.com/ap/oa?'
        loginURL = loginURL + 'client_id=' + self.APP_ID + '&'
        loginURL = loginURL + 'scope=profile&'
        loginURL = loginURL + 'redirect_uri=https%3A%2F%2F' + request.headers['Host'] + '%2Foauth2callback%2Famazon&'
        loginURL = loginURL + 'response_type=code'
        return loginURL
        
    def doGetToken(self,code):
        import httplib, urllib
    
        host = 'api.amazon.com'
        path = '/auth/o2/token'
    
        data = 'grant_type=authorization_code'
        data = data + '&code=' + code 
        data = data + '&redirect_uri=https%3A%2F%2F' + request.headers['Host'] + '%2Foauth2callback%2Famazon'
        data = data + '&client_id=' + self.APP_ID
        data = data + '&client_secret=' + self.APP_SECRET

        headers = {'Content-type': 'application/x-www-form-urlencoded'}
    
        conn = httplib.HTTPSConnection(host)
        conn.request('POST', path, data, headers)
        resp = conn.getresponse()
        return json.loads(resp.read())
    
    def doGetUserProfile(self,token):
        import urllib2, json
        
        url = 'https://api.amazon.com/user/profile?'
        url = url + '&access_token=' + token
    
        response = urllib2.urlopen(url)
        amazonProfile = json.loads(response.read())
        #print '--- amazonProfile : ' + str(amazonProfile)
    
        return { 'name' : amazonProfile['name'], 'firstname' : amazonProfile['name'].split()[0],
                 'email' : amazonProfile['email'], 'picture' : '/static/img/amazon-logo-50.png',
                 'provider' : 'Amazon'}
    
    def getRoleARN(self):
        return self.ROLE_ARN        
    