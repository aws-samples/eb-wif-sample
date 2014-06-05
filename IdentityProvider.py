
def getIdentityProvider(provider, appID, appSecret, roleARN):
    
    from AmazonIdentityProvider   import AmazonIdentityProvider
    from FacebookIdentityProvider import FacebookIdentityProvider
    from GoogleIdentityProvider   import GoogleIdentityProvider
    
    ip = None
    if provider == 'google':
        ip = GoogleIdentityProvider(appID, appSecret, roleARN)  
    elif provider == 'facebook':
        ip = FacebookIdentityProvider(appID, appSecret, roleARN)
    elif provider == 'amazon':
        ip = AmazonIdentityProvider(appID, appSecret, roleARN)
        
    assert ip != None
    
    return ip
    
class IdentityProvider:

    APP_ID      = None
    APP_SECRET  = None
    ROLE_ARN    = None

    def __init__(self, appID, appSecret, roleARN):
        self.APP_ID      = appID
        self.APP_SECRET  = appSecret
        self.ROLE_ARN    = roleARN
            
    def oauthCallback(self,code):
            # echange authorization code  
            print '--- exchanging token for code : ' + code  
            token = self.doGetToken(code)
            print '--- received token : ' + str(token)

            # Call user service
            print '--- Getting user Profile for access_token : ' + self.getAccessToken(token)
            profile = self.doGetUserProfile(self.getAccessToken(token))
            print '--- received profile : ' + str(profile)

            # call AWS STS 
            print '--- Getting AWS Temp Credentials for token : ' + self.getIDToken(token)
            credentials = self.doGetAccessCredentials(self.getIDToken(token), profile)
            print '--- received credentials : ' + str(credentials)
        
            return credentials, profile
    
    def getAccessToken(self, token):
        # default for all except FaceBook
        return token['access_token']
        
    def getIDToken(self,token):    
        # default for all, except Google, Facebook
        return token['access_token']
        
    def loginURL(self):
        raise NotImplementedError("Please Implement this method in subclasses")
        
    def doGetToken(self,code):
        raise NotImplementedError("Please Implement this method in subclasses")
        
    def doGetUserProfile(self,token):
        raise NotImplementedError("Please Implement this method in subclasses")
        
    def getRoleARN(self):
        raise NotImplementedError("Please Implement this method in subclasses")

    def doGetAccessCredentials(self, token, profile):
        from boto.sts.connection import STSConnection

        conn = STSConnection(anon=True, debug=1)

        roleARN = self.getRoleARN()
        email   = profile['email'][:32] # Max 32 characters

        providerID = ''
        if profile['provider'] == 'Facebook':
            providerID = 'graph.facebook.com'
        elif profile['provider'] == 'Amazon':
            providerID = 'www.amazon.com'

        if providerID == '':
            assumedRole = conn.assume_role_with_web_identity(role_arn=roleARN,
                                                             role_session_name=email,
                                                             web_identity_token=token)
        else:
            assumedRole = conn.assume_role_with_web_identity(role_arn=roleARN,
                                                             role_session_name=email,
                                                             web_identity_token=token,
                                                             provider_id=providerID)

        return assumedRole.credentials.to_dict()

    # def doGetAccessCredentials_NO_BOTO(self, token, profile):
    #     import urllib, urllib2, json
    #
    #     # Let's subclass give us the role ARN
    #     roleARN = self.getRoleARN()
    #     email   = profile['email']
    #
    #     url = 'https://sts.amazonaws.com?Action=AssumeRoleWithWebIdentity'
    #     url = url + '&DurationSeconds=3600'
    #     url = url + '&RoleSessionName=' + email
    #     url = url + '&Version=2011-06-15'
    #     url = url + '&RoleArn=' + roleARN
    #     url = url + '&WebIdentityToken=' + token
    #
    #     if profile['provider'] == 'Facebook':
    #         url = url + '&ProviderId=graph.facebook.com'
    #     elif profile['provider'] == 'Amazon':
    #         url = url + '&ProviderId=www.amazon.com'
    #
    #     request = urllib2.Request(url, headers= {'Accept' : 'application/json'} )
    #     response = urllib2.urlopen(request)
    #     assumedRole = response.read()
    #     assumedRole = json.loads(assumedRole)
    #     return assumedRole['AssumeRoleWithWebIdentityResponse']['AssumeRoleWithWebIdentityResult']['Credentials']
        