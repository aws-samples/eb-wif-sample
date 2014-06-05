import json
from IdentityProvider import IdentityProvider 
from flask import request

class FacebookIdentityProvider(IdentityProvider):

    def getAccessToken(self, token):
        return token['access_token'][0]
        
    def getIDToken(self,token):    
        return token['access_token'][0]
           
    def loginURL(self):
        loginURL = 'https://www.facebook.com/dialog/oauth?'
        loginURL = loginURL + 'client_id=' + self.APP_ID + '&'
        loginURL = loginURL + 'scope=email&'
        loginURL = loginURL + 'redirect_uri=https%3A%2F%2F' + request.headers['Host'] + '%2Foauth2callback%2Ffacebook'
        return loginURL
        
    def doGetToken(self,code):
        import urllib, urllib2, urlparse
    
        url = 'https://graph.facebook.com/oauth/access_token?'
        url = url + '&client_id=' + self.APP_ID
        url = url + '&redirect_uri=https%3A%2F%2F' + request.headers['Host'] + '%2Foauth2callback%2Ffacebook'
        url = url + '&client_secret=' + self.APP_SECRET
        url = url + '&code=' + code

        FBrequest = urllib2.Request(url, headers= {'Accept' : 'application/json'} )
        response = urllib2.urlopen(FBrequest)
        token = response.read()
        return urlparse.parse_qs(token)
        
    def doGetUserProfile(self,token):
        import urllib2, json
        url = 'https://graph.facebook.com/me?'
        url = url + '&fields=name,email,first_name,picture'
        url = url + '&access_token=' + token
    
        response = urllib2.urlopen(url)
        facebookProfile = json.loads(response.read())
        #print '--- facebookProfile : ' + str(facebookProfile)
    
        return { 'name' : facebookProfile['name'], 'firstname' : facebookProfile['first_name'],
                 'email' : facebookProfile['email'], 'picture' : facebookProfile['picture']['data']['url'],
                 'provider' : 'Facebook'}

    def getRoleARN(self):
        return self.ROLE_ARN       
