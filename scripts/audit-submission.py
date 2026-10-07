import runpy, json, pathlib, hashlib
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
for field in ['demoAccountName','demoAccountPassword']:
    report['review']['attributes'][field] = bool(report['review']['attributes'].get(field))
report['screenshots']=[]
for loc in report['localizations']:
    for group in api('GET','appStoreVersionLocalizations/'+loc['id']+'/appScreenshotSets')['data']:
        images=api('GET','appScreenshotSets/'+group['id']+'/appScreenshots')['data']
        expected=pathlib.Path('approved-screenshots')/('iphone-homepage.png' if group['attributes']['screenshotDisplayType']=='APP_IPHONE_67' else 'ipad-homepage.png')
        checksum=hashlib.md5(expected.read_bytes()).hexdigest()
        keep=[i for i in images if i['attributes'].get('sourceFileChecksum')==checksum and i['attributes']['assetDeliveryState']['state']=='COMPLETE']
        if keep:
            for image in images:
                if image['id']!=keep[0]['id'] and image['attributes']['fileName']==expected.name:
                    api('DELETE','appScreenshots/'+image['id'])
            images=api('GET','appScreenshotSets/'+group['id']+'/appScreenshots')['data']
        report['screenshots'].append({'display':group['attributes']['screenshotDisplayType'],'images':[{'id':i['id'],'file':i['attributes']['fileName'],'state':i['attributes']['assetDeliveryState']} for i in images]})
report['appInfos']=api('GET','apps/'+app['id']+'/appInfos')['data']
for info in report['appInfos']:
    try:
        age=api('GET','appInfos/'+info['id']+'/ageRatingDeclaration')['data']
        attributes={k:'NONE' for k in ['alcoholTobaccoOrDrugUseOrReferences','contests','gamblingSimulated','gunsOrOtherWeapons','medicalOrTreatmentInformation','profanityOrCrudeHumor','sexualContentGraphicAndNudity','sexualContentOrNudity','horrorOrFearThemes','matureOrSuggestiveThemes','violenceCartoonOrFantasy','violenceRealisticProlongedGraphicOrSadistic','violenceRealistic']}
        attributes.update({'advertising':True,'gambling':False,'healthOrWellnessTopics':False,'lootBox':False,'messagingAndChat':True,'parentalControls':False,'ageAssurance':False,'socialMedia':False,'socialMediaAgeRestricted':False,'unrestrictedWebAccess':False,'userGeneratedContent':True})
        report['ageRating']=api('PATCH','ageRatingDeclarations/'+age['id'],{'data':{'type':'ageRatingDeclarations','id':age['id'],'attributes':attributes}})['data']
    except RuntimeError as e: report['ageRatingError']=str(e)
for route in ['apps/'+app['id']+'/appAvailabilityV2','apps/'+app['id']+'/appPriceSchedule']:
    try: report[route]=api('GET',route)['data']
    except RuntimeError as e: report[route]={'error':str(e)}
pathlib.Path('store-artifacts/submission-audit.json').write_text(json.dumps(report,indent=2))
print('Selected validated build 2; verified screenshot states:')
for item in report['screenshots']: print(json.dumps(item))
print('Version state: '+report['version']['attributes']['appStoreState'])
