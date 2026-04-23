# Mobile Integration Guide: DeepFit

## 1. Android (Google Assistant) Setup
### Configuration
- Move `shortcuts.xml` to `app/src/main/res/xml/`.
- Ensure `AndroidManifest.xml` has the `<meta-data>` tag pointing to `@xml/shortcuts`.
- Update `MainActivity.kt` package name to match your actual package.

### Testing with App Actions Test Tool
1. Install the **App Actions Test Tool** plugin in Android Studio.
2. Go to **Tools > App Actions > App Actions Test Tool**.
3. Select your `shortcuts.xml` file.
4. Click **Create Preview**.
5. On your test device (logged into the same Google account), say: *"Hey Google, open [Feature] in DeepFit"*.

---

## 2. iOS (Siri) Setup
### Xcode Configuration
1. **Capabilities**: In your Target settings, go to **Signing & Capabilities** and add **Siri**.
2. **Info.plist**: Add the key `NSSiriUsageDescription` with a string value like *"DeepFit uses Siri to let you start workouts with your voice."*

### Testing
1. Build and run the app on an iOS device or Simulator (running iOS 16+).
2. Open the **Shortcuts** app; you should see "DeepFit" listed under the App Shortcuts section.
3. Test by saying: *"Hey Siri, Open DeepFit"* or *"Hey Siri, Start my workout in DeepFit"*.

---

## 3. WebView Integration & Networking
Both platforms now use a WebView to load your existing Flask app. 

### Development URLs:
- **Android Emulator**: `http://10.0.2.2:5000` (Maps to your laptop's localhost).
- **iOS Simulator**: `http://localhost:5000`.
- **Physical Devices**: You **must** use your laptop's local network IP (e.g., `http://192.168.1.5:5000`).

### Critical Settings:
- **Android**: Ensure `INTERNET` permission is in `AndroidManifest.xml`:
  `<uses-permission android:name="android.permission.INTERNET" />`
- **iOS**: If using `http` (not `https`), you must allow "Arbitrary Loads" in `Info.plist`:
  ```xml
  <key>NSAppTransportSecurity</key>
  <dict>
      <key>NSAllowsArbitraryLoads</key>
      <true/>
  </dict>
  ```

## 4. General Checklist
- [ ] Verify app opens from a cold start (app was closed).
- [ ] Verify app handles the intent when already running in the background.
- [ ] Test on multiple screen sizes (Phones, Tablets, and macOS for Siri).
- [ ] Ensure `targetPackage` and `targetClass` in Android match your project's `build.gradle`.
- [ ] Verify the Flask server is running before launching the mobile app.

