import 'package:flutter/material.dart';
import 'login_screen.dart';
import 'scan_screen.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: const Color(0xfff4f7f1),
        body: SafeArea(child: Padding(padding: const EdgeInsets.all(24), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Spacer(),
          Container(width: 48, height: 48, alignment: Alignment.center, decoration: BoxDecoration(color: const Color(0xff14231d), borderRadius: BorderRadius.circular(14)), child: const Text('R', style: TextStyle(color: Color(0xffd8f36a), fontSize: 26, fontWeight: FontWeight.bold))),
          const SizedBox(height: 28),
          const Text('See what your crop is telling you.', style: TextStyle(fontSize: 42, height: 1.02, fontWeight: FontWeight.bold, letterSpacing: -1.5)),
          const SizedBox(height: 18),
          const Text('Record a short soybean field video and get an evidence-based crop health signal.', style: TextStyle(fontSize: 17, height: 1.5, color: Color(0xff66766d))),
          const SizedBox(height: 34),
          SizedBox(width: double.infinity, child: FilledButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const LoginScreen())), child: const Text('Sign in to scan'))),
          const SizedBox(height: 12),
          SizedBox(width: double.infinity, child: OutlinedButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ScanScreen())), child: const Text('Explore a demo scan'))),
          const SizedBox(height: 20),
          const Text('AI indication, not confirmed diagnosis.', style: TextStyle(fontSize: 12, color: Color(0xff819087))),
          const Spacer(),
        ])),
      );
}

