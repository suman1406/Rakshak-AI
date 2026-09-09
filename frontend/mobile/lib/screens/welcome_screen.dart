import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../widgets/app_components.dart';
import 'authentication_screens.dart';
import 'onboarding_screens.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
          body: SafeArea(
              child: PageContent(children: [
        const SizedBox(height: 18),
        const Row(children: [
          Icon(Icons.spa_outlined, color: RakshakColors.ink, size: 30),
          SizedBox(width: 10),
          Flexible(
              child: Text('rakshak ai',
                  style: TextStyle(
                      fontSize: 25,
                      letterSpacing: -1,
                      fontWeight: FontWeight.w700,
                      color: RakshakColors.ink)))
        ]),
        const SizedBox(height: 28),
        ClipRRect(
            borderRadius: BorderRadius.circular(24),
            child: Image.asset('assets/soybean-field.png',
                height: 260,
                width: double.infinity,
                fit: BoxFit.cover,
                semanticLabel: 'Illustrative soybean field in morning light')),
        const SizedBox(height: 26),
        Text('Your field.\nA closer look.',
            style: Theme.of(context).textTheme.displaySmall?.copyWith(
                fontSize: 40,
                fontWeight: FontWeight.w700,
                letterSpacing: -1.5)),
        const SizedBox(height: 14),
        const Text(
            'Keep your field observations together. Record a short soybean video, read the evidence, and ask for an expert review.'),
        const SizedBox(height: 24),
        PrimaryAction(
            label: 'Create your farmer account',
            icon: Icons.arrow_forward,
            onPressed: () => navigateTo(context, const RegisterScreen())),
        const SizedBox(height: 12),
        SecondaryAction(
            label: 'Sign in',
            onPressed: () => navigateTo(context, const LoginScreen())),
        const SizedBox(height: 12),
        Center(
            child: TextButton(
                onPressed: () => navigateTo(context, const OnboardingScreen()),
                child: const Text('How field recording works'))),
        const SizedBox(height: 16),
        const Text('Soybean pilot. AI indications need human judgment.',
            style: TextStyle(fontSize: 13, color: RakshakColors.leaf)),
      ])));
}
