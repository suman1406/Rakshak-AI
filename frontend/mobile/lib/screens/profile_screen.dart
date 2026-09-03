import 'package:flutter/material.dart';
import '../api_client.dart';
import '../core/app_theme.dart';
import '../widgets/app_components.dart';
import 'welcome_screen.dart';

class ProfileScreen extends StatefulWidget { const ProfileScreen({super.key}); @override State<ProfileScreen> createState() => _ProfileScreenState(); }
class _ProfileScreenState extends State<ProfileScreen> {
  late Future<Map<String, dynamic>> profile;
  @override void initState() { super.initState(); profile = ApiClient.instance.currentUser(); }
  @override Widget build(BuildContext context) => FutureBuilder<Map<String, dynamic>>(future: profile, builder: (context, snapshot) {
    if (snapshot.connectionState != ConnectionState.done) return const Center(child: CircularProgressIndicator());
    if (snapshot.hasError) return PageContent(children: [Text('Profile & settings', style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 16), AppCard(child: Text('Could not load your profile. ${snapshot.error}')), const SizedBox(height: 12), PrimaryAction(label: 'Try again', onPressed: () => setState(() => profile = ApiClient.instance.currentUser()))]);
    final user = snapshot.data!; final name = user['display_name']?.toString() ?? user['email']?.toString() ?? user['phone']?.toString() ?? 'Account'; final role = user['role']?.toString() ?? 'farmer';
    return PageContent(children: [Text('Profile & settings', style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 20), AppCard(child: Row(children: [CircleAvatar(radius: 28, backgroundColor: RakshakColors.signal, child: Text(name.substring(0, 1).toUpperCase(), style: const TextStyle(color: RakshakColors.ink, fontSize: 22, fontWeight: FontWeight.w800))), const SizedBox(width: 14), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(name, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800)), Text(role)]))])), const SizedBox(height: 20), const AppCard(child: Text('Profile changes and notification preferences are not exposed by the current backend yet.')), const SizedBox(height: 20), SecondaryAction(label: 'Sign out', onPressed: () async { await ApiClient.instance.signOut(); if (context.mounted) Navigator.of(context).pushAndRemoveUntil(MaterialPageRoute(builder: (_) => const WelcomeScreen()), (_) => false); })]);
  });
}
