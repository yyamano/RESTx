"""
RESTx: Sane, simple and effective data publishing and integration. 

Copyright (C) 2010   MuleSoft Inc.    http://www.mulesoft.com

This program is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by 
the Free Software Foundation, either version 3 of the License, or 
(at your option) any later version. 

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details. 

You should have received a copy of the GNU General Public License 
along with this program.  If not, see <http://www.gnu.org/licenses/>. 

"""

import sys
import urllib
import simplejson as json

#
# For the TWITTER component:
#
# Specify the account name and password
#
TWITTER_ACCOUNT  = "##################"      # Replace those two with actual account credentials
TWITTER_PASSWORD = "***********"

#SERVER_URL = "http://mulesoft-restx.appspot.com"
#SERVER_URL = "http://localhost:8080"
SERVER_URL = "http://localhost:8001"




def json_pretty_print(json_str):
    obj = json.loads(json_str)
    print json.dumps(obj, indent=4)

#
# A URL opener and handler class
#
ERROR_INFO = None
class MyOpener(urllib.URLopener):
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        global ERROR_INFO
        ERROR_INFO = (errcode, errmsg, fp.read())
    def add_msg(self, message):
        if message:
            self._my_msg = message
            self.addheader('Content-length', str(len(message)))
    def send(self, code_url):
        if hasattr(self, "_my_msg"):
            msg = self._my_msg
            print "@@ POSTing to server: ", msg
        else:
            msg = None
        return self.open(code_url, msg)
        

#
# Post stuff to create a resource
#
def send_test(data, code_url):
    global ERROR_INFO
    print "="*80
    opener = MyOpener()
    opener.addheader('Connection', 'close')
    opener.addheader('Accept', 'application/json')
    if type(data) is str:
        opener.add_msg(data)
    else:
        opener.add_msg(json.dumps(data))
    stream = opener.send(code_url)
    
    is_stream = True
    """
    if ERROR_INFO[0] == 201:
        stream = ERROR_INFO[2]
        is_stream = False
    """
    if stream:
        if is_stream:
            data = stream.read()
        else:
            data = stream
        print "Received data: ", data
    else:
        print "ERROR: ", ERROR_INFO


print "\nCreating a few resources on the server...\n"

# Create the Twitter component
send_test({
            'params' : {
                "account_password" : TWITTER_PASSWORD,
                "account_name" :     TWITTER_ACCOUNT
             },
             "resource_creation_params" : {
                "suggested_name" : "%sTwitter" % TWITTER_ACCOUNT
             }
          },
          code_url=SERVER_URL + "/code/TwitterComponent")

send_test({
            'params' : {
                "account_password" : TWITTER_PASSWORD,
                "account_name" :     TWITTER_ACCOUNT
             },
             "resource_creation_params" : {
                "suggested_name" : "Java%sTwitter" % TWITTER_ACCOUNT
             }
          },
          code_url=SERVER_URL + "/code/JavaTwitterComponent")


# Create the Gsearch component
send_test({
            'params' : {
                'api_key' : "ABQIAAAApvtgUnVbhZ4o1RA5ncDnZhT2yXp_ZAY8_ufC3CFXhHIE1NvwkxS5mUUQ41lAGdMeNzzWizhSGRxfiA"
            },
            'resource_creation_params' : {
                'suggested_name' : 'MyGoogleSearch'
            }
          },
          code_url=SERVER_URL + "/code/GoogleSearchComponent")

# Create the Combiner component
send_test({
            'resource_creation_params' : {
                'suggested_name' : 'Combiner',
                'desc'           : "Just a test, don't use this one..."
            }
          },
          code_url=SERVER_URL + "/code/CombinerComponent")

# Create the GpsWalker component
send_test({
            'resource_creation_params' : {
                'suggested_name' : 'MyGPSWalker'
            }
          },
          code_url=SERVER_URL + "/code/GpsWalkerComponent")

# Create the Storage component
send_test({
            'resource_creation_params' : {
                'suggested_name' : 'MyStorageResource'
            },
          },
          code_url=SERVER_URL + "/code/StorageComponent")

# Create Java test component
send_test({
            'params' : {
                "api_key" : "Foobar",
            },
            'resource_creation_params' : {
                'suggested_name' : 'MyJavaTestComponent'
            },
          },
          code_url=SERVER_URL + "/code/TestComponent")

# Create another Storage component
send_test({
            'resource_creation_params' : {
                'suggested_name' : 'MySecondStorageResource'
            },
          },
          code_url=SERVER_URL + "/code/StorageComponent")
'''
# Create a Salesforce component
send_test({
            'params' : {
                'username'       : 'development@mulesoft.com.support',
                'password'       : 'mul3d3v201510',
                'security_token' : '9UUFx84vYkL1GcUPGOPQG0IfB',
                'API_URI'        : 'https://test.salesforce.com/services/Soap/u/16.0'
            },
            'resource_creation_params' : {
                'suggested_name' : 'MySalesforceResource'
            },
          },
          code_url=SERVER_URL + "/code/SalesforceComponent")

# Create a Marakana component
send_test({
            'params': {
                'salesforce_resource' : "/resource/MySalesforceResource"
            },
            'resource_creation_params' : {
                'suggested_name' : 'MyMarakanaResource'
            },
          },
          code_url=SERVER_URL + "/code/MarakanaComponent")

buf = """
<?xml version="1.0" encoding="UTF-8"?>
<spark-domain xmlns="http://marakana.com/xml/ns/spark/domain"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://marakana.com/xml/ns/spark/domain schema/domain_1.0.xml"
  version="1.0">

  <product-order id="723439" created="2010-03-15T09:15:05Z">
    <status>NEW</status>
    <customer id="541332" created="2010-03-15T09:15:05Z">
      <salutation>Mr.</salutation>
      <salutation>Mrs.</salutation>
      <salutation>Ms.</salutation>
      <first-name>Adam</first-name>
      <last-name>Watson</last-name>
      <organization-ref id="283190">ACME Inc.</organization-ref>
      <title>Software Developer</title>
      <office-phone>415-647-7000</office-phone>
      <email>m.rist@enbw.com</email>
      <address>
        <street1>1071 Mississippi St</street1>
        <city>San Francisco</city>
        <region>CA</region>
        <postal-code>94107</postal-code>
        <country>US</country>
        <type>BUSINESS</type>
      </address>
      <password-set>true</password-set>
      <enabled>true</enabled>
    </customer>
    <customer-organization-ref id="283190">ACME Inc.</customer-organization-ref>
    <coupon-discount>
      <coupon-ref id="872">W7S-8A1-X5Q-9X4</coupon-ref>
      <discount currency="USD">50.00</discount>
    </coupon-discount>
    <taxable-subtotal currency="USD">125.00</taxable-subtotal>
    <tax-rate>0.00</tax-rate>
    <credit-card-payment id="432523">
      <status>PROCESSED</status>
      <first-name>Tom</first-name>
      <last-name>Simon</last-name>
      <organization>ACME Inc.</organization>
      <phone>415-647-7001</phone>
      <address>
        <street1>1071 Mississippi St</street1>
        <city>San Francisco</city>
        <region>CA</region>
        <postal-code>94107</postal-code>
        <country>US</country>
        <type>BUSINESS</type>
      </address>
      <amount currency="USD">125.00</amount>
      <processed-amount currency="USD">125.00</processed-amount>
      <credit-card-type>VISA</credit-card-type>
      <credit-card-number>************1234</credit-card-number>
      <credit-card-processing-date>2010-03-15T09:15:08Z</credit-card-processing-date>
      <processing-confirmation>WSWX078VZKJ421NA7</processing-confirmation>
    </credit-card-payment>
    <product-item id="234232">
      <product-ref id="234">Learn How to Program in 24 Hours!</product-ref>
      <unit-price currency="USD">175.00</unit-price>
      <quantity>1</quantity>
      <download-count>0</download-count>
      <shipping-characteristics>
        <shipping-method>DOWNLOAD</shipping-method>
        <shipping-file-to-download>/static/premium/self-paced/234/v1/index.html</shipping-file-to-download>
        <shipping-max-download-days>90</shipping-max-download-days>
        <shipping-directory-download-enabled>true</shipping-directory-download-enabled>
      </shipping-characteristics>
    </product-item>
  </product-order>

</spark-domain>
"""
send_test(buf, code_url=SERVER_URL + "/resource/MyMarakanaResource/orders")


buf = """
<?xml version="1.0" encoding="UTF-8"?>
<spark-domain xmlns="http://marakana.com/xml/ns/spark/domain"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://marakana.com/xml/ns/spark/domain schema/domain_1.0.xml"
  version="1.0">

  <registration-order id="723432" created="2010-04-15T09:15:05Z">
    <status>NEW</status>
    <customer id="541332" created="2010-04-15T09:15:05Z">
      <salutation>Mr.</salutation>
      <first-name>Adam</first-name>
      <last-name>Watson</last-name>
      <organization-ref id="283190">ACME Inc.</organization-ref>
      <title>Software Developer</title>
      <office-phone>415-647-7000</office-phone>
      <email>adam.watson@acme.com</email>
      <address>
        <street1>1071 Mississippi St</street1>
        <city>San Francisco</city>
        <region>CA</region>
        <postal-code>94107</postal-code>
        <country>US</country>
        <type>BUSINESS</type>
      </address>
      <password-set>true</password-set>
      <enabled>true</enabled>
    </customer>
    <customer-organization-ref id="283190">ACME Inc.</customer-organization-ref>
    <coupon-discount>
      <coupon-ref id="873">Y7S-8A1-X5Q-9X9</coupon-ref>
      <discount currency="USD">100.00</discount>
    </coupon-discount>
    <taxable-subtotal currency="USD">1900.00</taxable-subtotal>
    <tax-rate>0.00</tax-rate>
    <credit-card-payment id="432523">
      <status>PROCESSED</status>
      <first-name>Tom</first-name>
      <last-name>Simon</last-name>
      <organization>ACME Inc.</organization>
      <phone>415-647-7001</phone>
      <address>
        <street1>1071 Mississippi St</street1>
        <city>San Francisco</city>
        <region>CA</region>
        <postal-code>94107</postal-code>
        <country>US</country>
        <type>BUSINESS</type>
      </address>
      <amount currency="USD">1900.00</amount>
      <processed-amount currency="USD">1900.00</processed-amount>
      <credit-card-type>VISA</credit-card-type>
      <credit-card-number>************1234</credit-card-number>
      <credit-card-processing-date>2010-04-15T09:15:08Z</credit-card-processing-date>
      <processing-confirmation>FSWE078VZKJ421NA8</processing-confirmation>
    </credit-card-payment>
    <registration id="8932123">
      <status>CONFIRMED</status>
      <participant-ref id="541332">Adam Watson</participant-ref>
      <course-event-ref id="912342">
        <start-time>2010-06-10T19:25:38Z</start-time>
        <status>TENTATIVE</status>
        <location-ref id="2">San Francisco</location-ref>
        <course-ref id="232">Introduction to Programming</course-ref>
        <provider-ref id="14">Super Training Inc.</provider-ref>
      </course-event-ref>
      <fee currency="USD">1000.00</fee>
    </registration>
    <registration id="8932124">
      <status>CONFIRMED</status>
      <participant id="541332">
        <salutation>Mrs.</salutation>
        <first-name>Anna</first-name>
        <last-name>Markova</last-name>
        <organization-ref id="283190">ACME Inc.</organization-ref>
        <title>Sr. Software Developer</title>
        <office-phone>415-647-7003</office-phone>
        <email>anna.markova@acme.com</email>
        <password-set>false</password-set>
        <enabled>true</enabled>
      </participant>
      <course-event-ref id="912342">
        <start-time>2010-06-10T19:25:38Z</start-time>
        <status>TENTATIVE</status>
        <location-ref id="2">San Francisco</location-ref>
        <course-ref id="232">Introduction to Programming</course-ref>
        <provider-ref id="14">Super Training Inc.</provider-ref>
      </course-event-ref>
      <fee currency="USD">1000.00</fee>
    </registration>
  </registration-order>
</spark-domain>
"""
send_test(buf, code_url=SERVER_URL + "/resource/MyMarakanaResource/orders")
'''

send_test("This is some text!", code_url=SERVER_URL + "/resource/MyStorageResource/files/foo")

print "\nDone..."
