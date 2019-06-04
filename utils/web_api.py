import json
import urllib.request


# Same as tech class, this is supposed to get some information from the web in json format to make it
# possible to work with it.

# Didn't make it in time either
class WebApi:

    def basic_request(self, url):
        req = urllib.request.Request(url)

        ##parsing response
        r = urllib.request.urlopen(req).read()
        return json.loads(r.decode('utf-8'))

    def wiki_page(self, page_name):
        pass

    def faq(self, sub_page=""):
        pass
