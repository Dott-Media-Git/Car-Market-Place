import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.carmmarketug.app',
  appName: 'CarmMarketUG',
  webDir: 'public',
  server: {
    url: 'https://app.dott-media.org',
    allowNavigation: ['app.dott-media.org'],
    cleartext: false,
  },
  android: {
    buildOptions: {
      releaseType: 'AAB',
    },
  },
};

export default config;
