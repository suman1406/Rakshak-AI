# Rakshak mobile

Flutter farmer app. The app starts with the welcome/onboarding screen and includes login, crop/field selection, native video capture, video upload, processing status, and the guarded crop-health report.

Run with a connected API using:

```bash
flutter pub get
flutter run --dart-define=API_BASE_URL=https://your-api.example.com
```

Camera and microphone access are requested only when recording. Gallery selection uses the platform media picker. Audio is not used for diagnosis.
