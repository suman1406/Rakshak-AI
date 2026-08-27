import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../widgets/app_components.dart';
import 'welcome_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});
  @override
  Widget build(BuildContext context) => PageContent(children: [
        Text('Profile & settings',
            style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 20),
        const AppCard(
            child: Row(children: [
          CircleAvatar(
              radius: 28,
              backgroundColor: RakshakColors.signal,
              child: Text('A',
                  style: TextStyle(
                      color: RakshakColors.ink,
                      fontSize: 22,
                      fontWeight: FontWeight.w800))),
          SizedBox(width: 14),
          Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('Arjun Kumar',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
            Text('Farmer · Demo organization')
          ])
        ])),
        const SizedBox(height: 20),
        for (final setting in [
          'Notifications',
          'Language · English',
          'Help & support',
          'Privacy and safety'
        ])
          Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: AppCard(
                  child: Row(children: [
                const Icon(Icons.settings_outlined, color: RakshakColors.leaf),
                const SizedBox(width: 12),
                Expanded(
                    child: Text(setting,
                        style: const TextStyle(fontWeight: FontWeight.w700))),
                const Icon(Icons.chevron_right)
              ]))),
        const SizedBox(height: 10),
        SecondaryAction(
            label: 'Sign out',
            onPressed: () => Navigator.of(context).pushAndRemoveUntil(
                MaterialPageRoute(builder: (_) => const WelcomeScreen()),
                (_) => false))
      ]);
}
