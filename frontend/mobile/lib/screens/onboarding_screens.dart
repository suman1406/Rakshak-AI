import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../widgets/app_components.dart';
import 'authentication_screens.dart';

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});
  @override
  Widget build(BuildContext context) => const OnboardingIntroScreen();
}

class OnboardingIntroScreen extends StatelessWidget {
  const OnboardingIntroScreen({super.key});
  @override
  Widget build(BuildContext context) => const _OnboardingPage(
        title: 'Walk through your field',
        body: 'Capture a short video while moving steadily across the crop.',
        icon: Icons.video_camera_back_outlined,
        nextLabel: 'Next',
        onNext: null,
      );
}

class OnboardingEvidenceScreen extends StatelessWidget {
  const OnboardingEvidenceScreen({super.key});
  @override
  Widget build(BuildContext context) => _OnboardingPage(
        title: 'More frames, more context',
        body: 'Rakshak compares multiple moments instead of one still image.',
        icon: Icons.grid_view_rounded,
        nextLabel: 'Next',
        onNext: () => navigateTo(context, const OnboardingNextStepsScreen()),
      );
}

class OnboardingNextStepsScreen extends StatelessWidget {
  const OnboardingNextStepsScreen({super.key});
  @override
  Widget build(BuildContext context) => _OnboardingPage(
        title: 'Clear next steps',
        body: 'See evidence, confidence, and what to do next in plain language.',
        icon: Icons.check_circle_outline,
        nextLabel: 'Go to my fields',
        onNext: () => navigateTo(context, const LoginScreen()),
      );
}

class _OnboardingPage extends StatelessWidget {
  const _OnboardingPage({required this.title, required this.body, required this.icon, required this.nextLabel, required this.onNext});
  final String title, body, nextLabel;
  final IconData icon;
  final VoidCallback? onNext;
  @override
  Widget build(BuildContext context) => AppPage(
        title: 'Getting started',
        onBack: () => Navigator.pop(context),
        child: PageContent(crossAxisAlignment: CrossAxisAlignment.center, children: [
          const SizedBox(height: 70),
          Container(width: 128, height: 128, decoration: BoxDecoration(color: RakshakColors.signal, borderRadius: BorderRadius.circular(38)), child: Icon(icon, color: RakshakColors.ink, size: 58)),
          const SizedBox(height: 28),
          Text(title, textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 14),
          Text(body, textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodyLarge),
          const SizedBox(height: 32),
          PrimaryAction(label: nextLabel, onPressed: onNext ?? () => navigateTo(context, const OnboardingEvidenceScreen())),
          const SizedBox(height: 12),
          TextButton(onPressed: () => navigateTo(context, const LoginScreen()), child: const Text('Skip for now')),
        ]),
      );
}
