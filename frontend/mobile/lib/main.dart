import 'package:flutter/material.dart';
import 'core/app_theme.dart';
import 'screens/welcome_screen.dart';

void main() => runApp(const RakshakApp());

class RakshakApp extends StatelessWidget {
  const RakshakApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Rakshak AI',
        debugShowCheckedModeBanner: false,
        theme: buildRakshakTheme(),
        home: const WelcomeScreen(),
      );
}
