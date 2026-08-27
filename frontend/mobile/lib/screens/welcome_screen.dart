import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../widgets/app_components.dart';
import 'authentication_screens.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
          body: SafeArea(
              child: PageContent(children: [
        const SizedBox(height: 34),
        Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
                color: RakshakColors.signal,
                borderRadius: BorderRadius.circular(20)),
            child: const Icon(Icons.eco_rounded,
                size: 42, color: RakshakColors.ink)),
        const SizedBox(height: 28),
        Text('Rakshak AI',
            style: Theme.of(context)
                .textTheme
                .titleMedium
                ?.copyWith(color: RakshakColors.leaf)),
        const SizedBox(height: 14),
        Text('See your crop\nwith more clarity.',
            style: Theme.of(context).textTheme.displaySmall),
        const SizedBox(height: 16),
        const Text(
            'Evidence-based crop health insights from a simple field video.'),
        const SizedBox(height: 28),
        const SafetyNote(
            title: 'Built for careful field decisions.',
            body:
                'Capture context, review evidence, and know when a second set of eyes is useful.'),
        const SizedBox(height: 24),
        PrimaryAction(
            label: 'Get started',
            icon: Icons.arrow_forward_rounded,
            onPressed: () => navigateTo(context, const LoginScreen())),
        const SizedBox(height: 12),
        SecondaryAction(
            label: 'Create an account',
            onPressed: () => navigateTo(context, const RegisterScreen())),
      ])));
}
