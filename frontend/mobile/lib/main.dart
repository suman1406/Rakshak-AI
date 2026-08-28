import 'package:flutter/material.dart';
import 'core/app_theme.dart';
import 'screens/welcome_screen.dart';
import 'screens/dashboard_screen.dart';
import 'api_client.dart';

void main() => runApp(const RakshakApp());

class RakshakApp extends StatelessWidget {
  const RakshakApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Rakshak AI',
        debugShowCheckedModeBanner: false,
        theme: buildRakshakTheme(),
        home: const SessionGate(),
      );
}

class SessionGate extends StatefulWidget {
  const SessionGate({super.key});
  @override State<SessionGate> createState() => _SessionGateState();
}

class _SessionGateState extends State<SessionGate> {
  late final Future<bool> session = ApiClient.instance.restoreSession();
  @override
  Widget build(BuildContext context) => FutureBuilder<bool>(
        future: session,
        builder: (context, snapshot) {
          if (!snapshot.hasData) return const Scaffold(body: Center(child: CircularProgressIndicator()));
          return snapshot.data! ? const HomeScreen() : const WelcomeScreen();
        },
      );
}
