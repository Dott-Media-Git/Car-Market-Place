import subprocess, json, time, pathlib
def run(*args):
    return subprocess.check_output(args, text=True).strip()
devices=json.loads(run('xcrun','simctl','list','devices','available','--json'))['devices']
all_devices=[d for ds in devices.values() for d in ds]
out=pathlib.Path('store-artifacts');out.mkdir(exist_ok=True)
for kind,match in [('iphone','Pro Max'),('ipad','iPad Pro 13')]:
    candidates=[d for d in all_devices if match in d['name']]
    if not candidates: raise RuntimeError('Missing simulator '+match)
    d=candidates[0];uid=d['udid']
    if kind=='iphone':
        runtimes=json.loads(run('xcrun','simctl','list','runtimes','--json'))['runtimes']
        runtime=next(r['identifier'] for r in runtimes if r.get('isAvailable') and r['name'].startswith('iOS 26'))
        uid=run('xcrun','simctl','create','CarMarketplace Clean iPhone','com.apple.CoreSimulator.SimDeviceType.iPhone-16-Pro-Max',runtime)
        d={'name':'Clean iPhone 16 Pro Max','state':'Shutdown'}
    if d['state']!='Booted': run('xcrun','simctl','boot',uid)
    run('xcrun','simctl','bootstatus',uid,'-b')
    run('xcrun','simctl','status_bar',uid,'override','--time','9:41','--batteryState','charged','--batteryLevel','100')
    run('xcrun','simctl','install',uid,'build/simulator/Build/Products/Debug-iphonesimulator/App.app')
    run('xcrun','simctl','launch',uid,'com.carmmarketug.app')
    time.sleep(120)
    if kind=='iphone':
        run('xcrun','simctl','terminate',uid,'com.carmmarketug.app')
        run('xcrun','simctl','launch',uid,'com.carmmarketug.app')
        time.sleep(60)
        logs=run('xcrun','simctl','spawn',uid,'log','show','--last','5m','--style','compact','--predicate','process == "App"')
        out.joinpath('iphone-runtime.log').write_text(logs)
    run('xcrun','simctl','io',uid,'screenshot',str(out/(kind+'-homepage.png')))
    run('xcrun','simctl','shutdown',uid)
    print('Captured actual app on '+d['name'])
