import runpy, pathlib, hashlib, time, requests
ctx=runpy.run_path('scripts/store-details.py')
api=ctx['api'];loc=ctx['report']['localizationId']
sets=api('GET','appStoreVersionLocalizations/'+loc+'/appScreenshotSets')['data']
for file,display in [('ipad-homepage.png','APP_IPAD_PRO_3GEN_129'),('iphone-homepage.png','APP_IPHONE_67')]:
    path=pathlib.Path('approved-screenshots')/file
    if not path.exists(): continue
    data=path.read_bytes();checksum=hashlib.md5(data).hexdigest()
    found=[s for s in sets if s['attributes']['screenshotDisplayType']==display]
    st=found[0] if found else api('POST','appScreenshotSets',{'data':{'type':'appScreenshotSets','attributes':{'screenshotDisplayType':display},'relationships':{'appStoreVersionLocalization':{'data':{'type':'appStoreVersionLocalizations','id':loc}}}}})['data']
    existing=api('GET','appScreenshotSets/'+st['id']+'/appScreenshots')['data']
    if any(x['attributes'].get('sourceFileChecksum')==checksum and x['attributes'].get('assetDeliveryState',{}).get('state')=='COMPLETE' for x in existing):
        print(file+' already uploaded');continue
    pending=[x for x in existing if x['attributes'].get('sourceFileChecksum')==checksum and x['attributes'].get('assetDeliveryState',{}).get('state')!='FAILED']
    asset=pending[0] if pending else api('POST','appScreenshots',{'data':{'type':'appScreenshots','attributes':{'fileName':file,'fileSize':len(data)},'relationships':{'appScreenshotSet':{'data':{'type':'appScreenshotSets','id':st['id']}}}}})['data']
    for op in ([] if pending else asset['attributes']['uploadOperations']):
        r=requests.request(op['method'],op['url'],headers={h['name']:h['value'] for h in op['requestHeaders']},data=data[op['offset']:op['offset']+op['length']],timeout=120)
        r.raise_for_status()
    if not pending:
        api('PATCH','appScreenshots/'+asset['id'],{'data':{'type':'appScreenshots','id':asset['id'],'attributes':{'uploaded':True,'sourceFileChecksum':checksum}}})
    for _ in range(90):
        state=api('GET','appScreenshots/'+asset['id'])['data']['attributes']['assetDeliveryState']
        if state['state']=='COMPLETE': break
        if state['state']=='FAILED': raise RuntimeError(str(state))
        time.sleep(5)
    assert state['state']=='COMPLETE', 'Screenshot still processing'
    for old in existing:
        if old['id']!=asset['id'] and old['attributes']['fileName']==file:
            api('DELETE','appScreenshots/'+old['id'])
    print(file+' uploaded and accepted')
