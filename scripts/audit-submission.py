import runpy, json, pathlib
c=runpy.run_path('scripts/store-details.py')
api=c['api'];app=c['app'];version=c['v'];report={}
builds=api('GET','builds?filter[app]='+app['id'])['data']
ready=[b for b in builds if b['attributes']['version']=='2' and b['attributes']['processingState']=='VALID']
assert len(ready)==1, 'Expected processed build 2'
api('PATCH','appStoreVersions/'+version['id']+'/relationships/build',{'data':{'type':'builds','id':ready[0]['id']}})
report['selectedBuild']={'id':ready[0]['id'],'version':'2','state':'VALID'}
report['version']=api('GET','appStoreVersions/'+version['id'])['data']
report['localizations']=api('GET','appStoreVersions/'+version['id']+'/appStoreVersionLocalizations')['data']
report['review']=api('GET','appStoreVersions/'+version['id']+'/appStoreReviewDetail')['data']
report['screenshots']=[]
for loc in report['localizations']:
    for group in api('GET','appStoreVersionLocalizations/'+loc['id']+'/appScreenshotSets')['data']:
        images=api('GET','appScreenshotSets/'+group['id']+'/appScreenshots')['data']
        report['screenshots'].append({'display':group['attributes']['screenshotDisplayType'],'images':[{'id':i['id'],'file':i['attributes']['fileName'],'state':i['attributes']['assetDeliveryState']} for i in images]})
report['appInfos']=api('GET','apps/'+app['id']+'/appInfos')['data']
for info in report['appInfos']:
    try: report['ageRating']=api('GET','appInfos/'+info['id']+'/ageRatingDeclaration')['data']
    except RuntimeError as e: report['ageRatingError']=str(e)
for route in ['apps/'+app['id']+'/appAvailabilityV2','apps/'+app['id']+'/appPriceSchedule']:
    try: report[route]=api('GET',route)['data']
    except RuntimeError as e: report[route]={'error':str(e)}
pathlib.Path('store-artifacts/submission-audit.json').write_text(json.dumps(report,indent=2))
print('Selected validated build 2; verified screenshot states:')
for item in report['screenshots']: print(json.dumps(item))
print('Version state: '+report['version']['attributes']['appStoreState'])
