import os, time, json, pathlib, base64
import jwt, requests

out = pathlib.Path('store-artifacts')
out.mkdir(exist_ok=True)
key = os.environ['APP_STORE_CONNECT_PRIVATE_KEY'].strip()
if key.startswith('@file:'):
    key = pathlib.Path(key[6:]).read_text()
elif not key.startswith('-----BEGIN'):
    if len(key)<1024 and pathlib.Path(key).is_file():
        key = pathlib.Path(key).read_text()
    else:
        key = base64.b64decode(key).decode()
key = key.replace('\\n','\n')
token = jwt.encode({'iss': os.environ['APP_STORE_CONNECT_ISSUER_ID'], 'iat': int(time.time()), 'exp': int(time.time())+1100, 'aud': 'appstoreconnect-v1'}, key, algorithm='ES256', headers={'kid': os.environ['APP_STORE_CONNECT_KEY_IDENTIFIER']})
s = requests.Session()
s.headers['Authorization'] = 'Bearer '+token
def api(method, route, payload=None):
    r = s.request(method, 'https://api.appstoreconnect.apple.com/v1/'+route, json=payload, timeout=90)
    if not r.ok:
        raise RuntimeError(str(r.status_code)+' '+r.text[:2000])
    return r.json() if r.content else {}
apps = api('GET', 'apps?filter[bundleId]=com.carmmarketug.app')['data']
assert len(apps)==1, 'Expected one CarMarketplace app'
app = apps[0]
versions = api('GET', 'apps/'+app['id']+'/appStoreVersions')['data']
builds = api('GET', 'builds?filter[app]='+app['id'])['data']
report = {'appId': app['id'], 'versions': versions, 'builds': builds}
description = '''Find your next vehicle and connect with car owners through CarMarketplace.

Browse vehicles for sale, view photos and details, and contact sellers. Publish your own vehicle for sale or rent and manage your listings from your dashboard.

Send rental inquiries to providers. Browse car parts, add items to your cart and send order requests to sellers.

Rental and parts requests require confirmation from the provider or seller. The app does not collect online payment for these requests.

Support: info@dottmedia.org'''
editable = [v for v in versions if v['attributes']['appStoreState'] in ['PREPARE_FOR_SUBMISSION','DEVELOPER_REJECTED','REJECTED']]
assert len(editable)==1, 'Expected one editable store version'
v = editable[0]
locales = api('GET', 'appStoreVersions/'+v['id']+'/appStoreVersionLocalizations')['data']
for loc in locales:
    if loc['attributes']['locale'].startswith('en'):
        api('PATCH', 'appStoreVersionLocalizations/'+loc['id'], {'data': {'type':'appStoreVersionLocalizations','id':loc['id'],'attributes':{'description':description,'keywords':'cars,Uganda,vehicles,buy,sell,rent,rentals,auto,parts,marketplace'}}})
        report['localizationId'] = loc['id']
        report['screenshotSets'] = api('GET','appStoreVersionLocalizations/'+loc['id']+'/appScreenshotSets')['data']
try:
    report['reviewDetail'] = api('GET','appStoreVersions/'+v['id']+'/appStoreReviewDetail')
except RuntimeError as error:
    report['reviewDetailError'] = str(error)
out.joinpath('store-status.json').write_text(json.dumps(report, indent=2))
print('Updated English description and keywords; stored review readiness report for app '+app['id'])
