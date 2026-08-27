import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import '../demo_data.dart';

const ink = Color(0xff14231d),
    canvas = Color(0xfff7faf4),
    muted = Color(0xff526259),
    lime = Color(0xffd4ee66),
    border = Color(0xffdfe7dc),
    healthy = Color(0xffe6f0d8),
    warning = Color(0xffb86b36);
void openPage(BuildContext c, Widget p) =>
    Navigator.push(c, MaterialPageRoute(builder: (_) => p));
Widget content(Widget w) =>
    SingleChildScrollView(padding: const EdgeInsets.all(16), child: w);
Widget card(Widget w) => Container(
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: border),
        borderRadius: BorderRadius.circular(16)),
    child: w);

class Frame extends StatelessWidget {
  const Frame({super.key, required this.title, required this.child, this.back});
  final String title;
  final Widget child;
  final VoidCallback? back;
  @override
  Widget build(BuildContext c) => Scaffold(
      appBar: AppBar(
          backgroundColor: canvas,
          surfaceTintColor: Colors.transparent,
          leading: back == null
              ? null
              : IconButton(onPressed: back, icon: const Icon(Icons.arrow_back)),
          title: Text(title,
              style: const TextStyle(color: ink, fontWeight: FontWeight.w800)),
          centerTitle: true),
      body: SafeArea(
          child: Center(
              child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 560),
                  child: child))));
}

class MainButton extends StatelessWidget {
  const MainButton(this.label, this.action, {super.key});
  final String label;
  final VoidCallback? action;
  @override
  Widget build(BuildContext c) => SizedBox(
      width: double.infinity,
      height: 52,
      child: FilledButton(
          onPressed: action,
          style: FilledButton.styleFrom(
              backgroundColor: lime, foregroundColor: ink),
          child: Text(label,
              style: const TextStyle(fontWeight: FontWeight.w800))));
}

class AltButton extends StatelessWidget {
  const AltButton(this.label, this.action, {super.key});
  final String label;
  final VoidCallback? action;
  @override
  Widget build(BuildContext c) => SizedBox(
      width: double.infinity,
      height: 52,
      child: OutlinedButton(
          onPressed: action,
          child: Text(label,
              style:
                  const TextStyle(color: ink, fontWeight: FontWeight.w800))));
}

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});
  @override
  Widget build(BuildContext c) => Scaffold(
          body: SafeArea(
              child: content(Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
            const SizedBox(height: 36),
            const Icon(Icons.eco, color: ink, size: 64),
            const SizedBox(height: 24),
            const Text('Rakshak AI',
                style: TextStyle(
                    color: muted, fontSize: 18, fontWeight: FontWeight.w800)),
            const SizedBox(height: 16),
            const Text('See your crop\nwith more clarity.',
                style: TextStyle(
                    color: ink, fontSize: 40, fontWeight: FontWeight.w800)),
            const SizedBox(height: 16),
            const Text(
                'Evidence-based crop health insights from a simple field video.',
                style: TextStyle(color: muted, fontSize: 18)),
            const SizedBox(height: 32),
            card(const Text(
                'Multi-frame analysis built for real field conditions.',
                style: TextStyle(color: ink, fontWeight: FontWeight.w700))),
            const SizedBox(height: 24),
            MainButton('Get started', () => openPage(c, const LoginScreen())),
            const SizedBox(height: 12),
            AltButton(
                'Create an account', () => openPage(c, const RegisterScreen()))
          ]))));
}

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});
  @override
  Widget build(BuildContext c) => Frame(
      title: 'Welcome back',
      back: () => Navigator.pop(c),
      child: content(
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Sign in to your fields',
            style: TextStyle(
                color: ink, fontSize: 28, fontWeight: FontWeight.w800)),
        const SizedBox(height: 24),
        const TextField(
            decoration: InputDecoration(labelText: 'Email address')),
        const SizedBox(height: 14),
        const TextField(
            obscureText: true,
            decoration: InputDecoration(labelText: 'Password')),
        const SizedBox(height: 24),
        MainButton('Sign in', () => openPage(c, const HomeScreen())),
        const SizedBox(height: 12),
        AltButton(
            'Create an account', () => openPage(c, const RegisterScreen())),
        const SizedBox(height: 20),
        card(const Text('Demo access: any input is accepted.',
            style: TextStyle(color: muted)))
      ])));
}

class RegisterScreen extends StatelessWidget {
  const RegisterScreen({super.key});
  @override
  Widget build(BuildContext c) => Frame(
      title: 'Create account',
      back: () => Navigator.pop(c),
      child: content(Column(children: [
        const TextField(decoration: InputDecoration(labelText: 'Full name')),
        const SizedBox(height: 14),
        const TextField(decoration: InputDecoration(labelText: 'Phone number')),
        const SizedBox(height: 14),
        const TextField(
            decoration: InputDecoration(labelText: 'Email address')),
        const SizedBox(height: 24),
        MainButton('Continue', () => openPage(c, const OnboardingScreen()))
      ])));
}

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});
  @override
  Widget build(BuildContext c) => Frame(
      title: 'Getting started',
      child: content(Column(children: [
        card(const Text(
            '1  Walk through your field\n\nCapture a short, steady video.',
            style: TextStyle(color: ink, fontSize: 18, height: 1.4))),
        const SizedBox(height: 12),
        card(const Text(
            '2  More frames, more context\n\nRakshak compares multiple moments.',
            style: TextStyle(color: ink, fontSize: 18, height: 1.4))),
        const SizedBox(height: 12),
        card(const Text(
            '3  Clear next steps\n\nSee evidence, confidence, and recommendations.',
            style: TextStyle(color: ink, fontSize: 18, height: 1.4))),
        const SizedBox(height: 24),
        MainButton('Go to my fields', () => openPage(c, const HomeScreen()))
      ])));
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeState();
}

class _HomeState extends State<HomeScreen> {
  int tab = 0;
  @override
  Widget build(BuildContext c) {
    final pages = [
      _Dashboard(
          onScan: () => openPage(c, const NewScanScreen()),
          onField: () => openPage(c, const FieldDetailsScreen())),
      const ScanHistoryScreen(),
      const ProfileScreen()
    ];
    return Scaffold(
        body: SafeArea(child: pages[tab]),
        bottomNavigationBar: NavigationBar(
            selectedIndex: tab,
            onDestinationSelected: (v) => setState(() => tab = v),
            destinations: const [
              NavigationDestination(
                  icon: Icon(Icons.home_outlined), label: 'Home'),
              NavigationDestination(
                  icon: Icon(Icons.history), label: 'History'),
              NavigationDestination(
                  icon: Icon(Icons.person_outline), label: 'Profile')
            ]));
  }
}

class _Dashboard extends StatelessWidget {
  const _Dashboard({required this.onScan, required this.onField});
  final VoidCallback onScan, onField;
  @override
  Widget build(BuildContext c) =>
      content(Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const SizedBox(height: 16),
        const Text('Good morning,', style: TextStyle(color: muted)),
        const Text('Arjun',
            style: TextStyle(
                color: ink, fontSize: 32, fontWeight: FontWeight.w800)),
        const SizedBox(height: 24),
        const Text('Your fields',
            style: TextStyle(
                color: ink, fontSize: 20, fontWeight: FontWeight.w800)),
        const SizedBox(height: 12),
        field(c, demoFields[0]),
        field(c, demoFields[1]),
        const SizedBox(height: 8),
        MainButton('Start a new scan', onScan),
        const SizedBox(height: 24),
        const Text('Recent scans',
            style: TextStyle(
                color: ink, fontSize: 20, fontWeight: FontWeight.w800)),
        const SizedBox(height: 12),
        for (final scan in demoScans)
          card(InkWell(
              onTap: () => openPage(c, const ReportScreen()),
              child: Text(
                  '${scan.disease}\n${scan.field} · ${scan.date}\n${scan.confidence}% confidence',
                  style: const TextStyle(color: ink, height: 1.5))))
      ]));
  Widget field(BuildContext c, DemoField f) => Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: InkWell(
          onTap: onField,
          child: card(
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(f.name,
                style:
                    const TextStyle(color: ink, fontWeight: FontWeight.w800)),
            Text(f.crop, style: const TextStyle(color: muted)),
            const SizedBox(height: 12),
            LinearProgressIndicator(
                value: f.health / 100,
                color: f.health > 80 ? muted : warning,
                backgroundColor: border)
          ]))));
}

class FieldDetailsScreen extends StatelessWidget {
  const FieldDetailsScreen({super.key});
  @override
  Widget build(BuildContext c) => Frame(
      title: 'North plot',
      back: () => Navigator.pop(c),
      child: content(
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        card(const Text('North plot\nSoybean · 4.2 acres',
            style: TextStyle(
                color: ink, fontSize: 21, fontWeight: FontWeight.w800))),
        const SizedBox(height: 16),
        card(const Text(
            '72%\nCurrent health score\n\nSoybean rust signal in multiple frames.\n87% confidence',
            style: TextStyle(color: muted, fontSize: 17, height: 1.5))),
        const SizedBox(height: 22),
        MainButton('Scan this field', () => openPage(c, const NewScanScreen()))
      ])));
}

class NewScanScreen extends StatefulWidget {
  const NewScanScreen({super.key});
  @override
  State<NewScanScreen> createState() => _NewScanState();
}

class _NewScanState extends State<NewScanScreen> {
  String? file;
  bool consent = false;
  Future<void> choose() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.video);
    if (result != null) setState(() => file = result.files.single.name);
  }

  @override
  Widget build(BuildContext c) => Frame(
      title: 'New scan',
      back: () => Navigator.pop(c),
      child: content(
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Capture a clear view',
            style: TextStyle(
                color: ink, fontSize: 28, fontWeight: FontWeight.w800)),
        const SizedBox(height: 22),
        const TextField(
            decoration:
                InputDecoration(labelText: 'Crop', hintText: 'Soybean')),
        const SizedBox(height: 14),
        const TextField(
            decoration:
                InputDecoration(labelText: 'Field', hintText: 'North plot')),
        const SizedBox(height: 18),
        card(Column(children: [
          Icon(
              file == null
                  ? Icons.video_file_outlined
                  : Icons.check_circle_outline,
              color: muted,
              size: 42),
          Text(file ?? 'No video selected',
              style: const TextStyle(color: ink, fontWeight: FontWeight.w700)),
          const SizedBox(height: 12),
          AltButton('Choose video', choose),
          AltButton('Record in app',
              () => openPage(context, const CameraGuidanceScreen())),
          TextButton(
              onPressed: () => setState(() => file = 'north_plot_demo.mp4'),
              child: const Text('Use demo video'))
        ])),
        CheckboxListTile(
            contentPadding: EdgeInsets.zero,
            value: consent,
            onChanged: (v) => setState(() => consent = v ?? false),
            title: const Text(
                'Decision support only; not a confirmed diagnosis.',
                style: TextStyle(color: muted, fontSize: 13)),
            controlAffinity: ListTileControlAffinity.leading),
        MainButton(
            'Continue to quality check',
            file != null && consent
                ? () => openPage(c, const VideoQualityScreen())
                : null)
      ])));
}

class CameraGuidanceScreen extends StatelessWidget {
  const CameraGuidanceScreen({super.key});
  @override
  Widget build(BuildContext c) => Frame(
      title: 'Camera guidance',
      child: Column(children: [
        Expanded(
            child: Container(
                color: ink,
                child: const Center(
                    child: Icon(Icons.eco, color: lime, size: 90)))),
        Padding(
            padding: const EdgeInsets.all(20),
            child: MainButton(
                'Capture video', () => openPage(c, const VideoQualityScreen())))
      ]));
}

class VideoQualityScreen extends StatelessWidget {
  const VideoQualityScreen({super.key});
  @override
  Widget build(BuildContext c) => Frame(
      title: 'Video quality check',
      child: content(Column(children: [
        card(const Text(
            'Video ready to analyze\n\n✓ Good lighting\n✓ Steady movement\n✓ Crop visible across frames',
            style: TextStyle(color: ink, fontSize: 17, height: 1.5))),
        const SizedBox(height: 22),
        MainButton(
            'Start analysis', () => openPage(c, const AnalyzingScreen())),
        TextButton(
            onPressed: () => openPage(c, const QualityFailedScreen()),
            child: const Text('Preview failed state'))
      ])));
}

class QualityFailedScreen extends StatelessWidget {
  const QualityFailedScreen({super.key});
  @override
  Widget build(BuildContext c) => Frame(
      title: 'Try another video',
      child: content(Column(children: [
        const SizedBox(height: 80),
        const Icon(Icons.videocam_off_outlined, color: warning, size: 76),
        const SizedBox(height: 20),
        const Text('We could not use this video',
            textAlign: TextAlign.center,
            style: TextStyle(
                color: ink, fontSize: 27, fontWeight: FontWeight.w800)),
        const SizedBox(height: 12),
        const Text(
            'Try better light, slower movement, and keep the crop visible.',
            textAlign: TextAlign.center,
            style: TextStyle(color: muted)),
        const SizedBox(height: 24),
        MainButton('Try again', () => openPage(c, const NewScanScreen()))
      ])));
}

class AnalyzingScreen extends StatelessWidget {
  const AnalyzingScreen({super.key});
  @override
  Widget build(BuildContext c) => Frame(
      title: 'Analyzing crop health',
      child: content(Column(children: [
        const SizedBox(height: 40),
        const CircularProgressIndicator(color: ink),
        const SizedBox(height: 24),
        const Text('Reading your field…',
            style: TextStyle(
                color: ink, fontSize: 28, fontWeight: FontWeight.w800)),
        const SizedBox(height: 24),
        for (final step in [
          'Extracting frames',
          'Checking crop visibility',
          'Comparing health signals',
          'Preparing your report'
        ])
          ListTile(
              leading: const Icon(Icons.check_circle, color: ink),
              title: Text(step)),
        const SizedBox(height: 16),
        MainButton('View demo report', () => openPage(c, const ReportScreen()))
      ])));
}

class ReportScreen extends StatelessWidget {
  const ReportScreen({super.key});
  @override
  Widget build(BuildContext c) => Frame(
      title: 'Crop health report',
      back: () => Navigator.pop(c),
      child: content(
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        card(const Text(
            'Soybean rust\nNorth plot · Today, 09:42\n\n87% confidence across 18 usable frames',
            style: TextStyle(
                color: ink,
                fontSize: 22,
                fontWeight: FontWeight.w800,
                height: 1.4))),
        const SizedBox(height: 18),
        const Text('What we saw',
            style: TextStyle(
                color: ink, fontSize: 20, fontWeight: FontWeight.w800)),
        const SizedBox(height: 10),
        card(const Text(
            'A similar signal appeared across multiple leaves. This is an indication for review, not a confirmed diagnosis.',
            style: TextStyle(color: muted, height: 1.4))),
        const SizedBox(height: 18),
        const Text('Evidence frames',
            style: TextStyle(
                color: ink, fontSize: 20, fontWeight: FontWeight.w800)),
        const SizedBox(height: 10),
        SizedBox(
            height: 90,
            child: Row(children: [
              for (var i = 0; i < 4; i++)
                Expanded(
                    child: Container(
                        height: 90,
                        margin: const EdgeInsets.only(right: 6),
                        color: i.isEven ? border : healthy,
                        child: Center(child: Text('Frame ${i + 1}'))))
            ])),
        const SizedBox(height: 20),
        card(const Text(
            'Suggested next step\nWalk the north plot again in 3–5 days and consider agronomist review if the signal spreads.',
            style: TextStyle(color: muted, height: 1.4))),
        const SizedBox(height: 18),
        MainButton('Share feedback', () => openPage(c, const FeedbackScreen())),
        AltButton(
            'Preview healthy result', () => openPage(c, const HealthyScreen())),
        TextButton(
            onPressed: () => openPage(c, const UncertainScreen()),
            child: const Text('Preview uncertain result'))
      ])));
}

class HealthyScreen extends StatelessWidget {
  const HealthyScreen({super.key});
  @override
  Widget build(BuildContext c) => ResultScreen(
      title: 'Healthy crop',
      description: 'No significant disease signal was detected.',
      action: 'Scan another area');
}

class UncertainScreen extends StatelessWidget {
  const UncertainScreen({super.key});
  @override
  Widget build(BuildContext c) => ResultScreen(
      title: 'Needs a closer look',
      description: 'The signal is not strong enough for a reliable result.',
      action: 'Request review');
}

class ResultScreen extends StatelessWidget {
  const ResultScreen(
      {super.key,
      required this.title,
      required this.description,
      required this.action});
  final String title, description, action;
  @override
  Widget build(BuildContext c) => Frame(
      title: 'Crop health report',
      child: content(Column(children: [
        const SizedBox(height: 60),
        const Icon(Icons.check_circle_outline, color: ink, size: 80),
        const SizedBox(height: 22),
        Text(title,
            textAlign: TextAlign.center,
            style: const TextStyle(
                color: ink, fontSize: 30, fontWeight: FontWeight.w800)),
        const SizedBox(height: 12),
        Text(description,
            textAlign: TextAlign.center,
            style: const TextStyle(color: muted, fontSize: 17)),
        const SizedBox(height: 24),
        card(const Text(
            'Try another scan in better light, or ask an agronomist to review the evidence frames.',
            style: TextStyle(color: muted))),
        const SizedBox(height: 22),
        MainButton(action, () => openPage(c, const NewScanScreen()))
      ])));
}

class FeedbackScreen extends StatelessWidget {
  const FeedbackScreen({super.key});
  @override
  Widget build(BuildContext c) => Frame(
      title: 'Share feedback',
      child: content(Column(children: [
        const Text('Was this helpful?',
            style: TextStyle(
                color: ink, fontSize: 28, fontWeight: FontWeight.w800)),
        const SizedBox(height: 24),
        card(const Text('How close was this result?\n\n☆  ☆  ☆  ☆  ☆',
            style: TextStyle(color: warning, fontSize: 24))),
        const SizedBox(height: 18),
        const TextField(
            maxLines: 4,
            decoration: InputDecoration(labelText: 'Add a note (optional)')),
        const SizedBox(height: 22),
        MainButton(
            'Submit feedback', () => openPage(c, const ReviewRequestedScreen()))
      ])));
}

class ReviewRequestedScreen extends StatelessWidget {
  const ReviewRequestedScreen({super.key});
  @override
  Widget build(BuildContext c) => Frame(
      title: 'Review requested',
      child: content(Column(children: [
        const SizedBox(height: 100),
        const Icon(Icons.mark_email_read_outlined, color: ink, size: 78),
        const SizedBox(height: 22),
        const Text('A second set of eyes is on it.',
            textAlign: TextAlign.center,
            style: TextStyle(
                color: ink, fontSize: 28, fontWeight: FontWeight.w800)),
        const SizedBox(height: 26),
        MainButton(
            'Back to my fields', () => Navigator.popUntil(c, (r) => r.isFirst))
      ])));
}

class ScanHistoryScreen extends StatelessWidget {
  const ScanHistoryScreen({super.key});
  @override
  Widget build(BuildContext c) =>
      content(Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const SizedBox(height: 16),
        const Text('Scan history',
            style: TextStyle(
                color: ink, fontSize: 30, fontWeight: FontWeight.w800)),
        const SizedBox(height: 20),
        for (final scan in demoScans)
          Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: InkWell(
                  onTap: () => openPage(c, const ReportScreen()),
                  child: card(Text(
                      '${scan.disease}\n${scan.field} · ${scan.date}\n${scan.confidence}% confidence',
                      style: const TextStyle(color: ink, height: 1.5)))))
      ]));
}

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});
  @override
  Widget build(BuildContext c) =>
      content(Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const SizedBox(height: 16),
        const Text('Profile & settings',
            style: TextStyle(
                color: ink, fontSize: 30, fontWeight: FontWeight.w800)),
        const SizedBox(height: 20),
        card(const Text('Arjun Kumar\nFarmer · Demo organization',
            style: TextStyle(color: ink, fontSize: 18, height: 1.5))),
        const SizedBox(height: 16),
        for (final value in [
          'Notifications',
          'Language · English',
          'Help & support',
          'Privacy and safety'
        ])
          Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: card(Text(value,
                  style: const TextStyle(
                      color: ink, fontWeight: FontWeight.w700)))),
        AltButton(
            'Sign out',
            () => Navigator.of(c).pushAndRemoveUntil(
                MaterialPageRoute(builder: (_) => const WelcomeScreen()),
                (_) => false))
      ]));
}
