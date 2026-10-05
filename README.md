# CarMarketplace iOS source

Prepared 2026-10-05. Version 1.1.0, initial iOS build 1. Bundle ID com.carmmarketug.app. Hosted app: https://app.dott-media.org.

This is source, not a signed IPA. No Mac compilation, device testing, signing, upload or App Store submission has run. Android signing files and backend credentials are excluded.

## Set up cloud build

1. Create a private GitHub repository from this folder. Include package-lock.json, ios, public, capacitor.config.ts and codemagic.yaml. Do not upload the original Android/backend project.
2. In Apple Developer, register the explicit bundle ID com.carmmarketug.app under your team if not already registered. In App Store Connect, create the iOS app record with that bundle ID and name CarMarketplace (subject to availability).
3. Connect the repository to Codemagic. In Team settings > Team integrations > Developer Portal, connect an App Store Connect API key using the integration name CarMarketplace Apple. Upload the .p8 key directly to Codemagic; do not commit it or send it in chat.
4. Configure an Apple Distribution certificate and App Store provisioning profile for this bundle ID in Codemagic signing settings. Follow https://docs.codemagic.io/yaml-code-signing/signing-ios/ . The YAML references these signing assets; it does not create them.
5. Select the ios-release workflow and start a manual build once account/signing setup is complete. Cloud service charges may apply under your account plan. It builds with Xcode 26 and uploads the binary to App Store Connect. It does not submit the app or external beta for review.
6. Start with IOS_BUILD_NUMBER 1 only if unused in App Store Connect; increase sequentially for each subsequent upload. Do not use date-based version codes.
7. Resolve Apple's processing/export-compliance questions accurately, then add internal TestFlight testers. Test sign-in, vehicle photo selection/camera, listing publishing, messaging, provider dashboard, rentals and parts order requests on iPhone. Test iPad too: this project supports both.

## Before App Store review

- Confirm a working support/privacy contact. Current hosted policy has an unverified privacy@carmarketplace.com address.
- Verify in-app account deletion and deletion of associated marketplace data. Clerk profile controls alone are not proof that listings/messages are deleted.
- Implement/verify user-generated-content reporting, blocking and moderation appropriate to Apple's guideline 1.2.
- Review privacy labels against actual Clerk authentication, hosted storage, photos, messages and any analytics. Do not declare that the app collects no data without an audit.
- Supply real device screenshots, accurate description/category/age rating, support and privacy URLs, and a reviewer account with access to relevant features.
- Review native usability and guideline 4.2; a hosted web wrapper is not guaranteed acceptance.
- Complete export-compliance declarations based on the app's actual encryption usage.

References: https://developer.apple.com/app-store/review/guidelines/ and https://docs.codemagic.io/yaml-publishing/app-store-connect/ .
