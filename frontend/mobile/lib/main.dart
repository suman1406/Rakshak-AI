import 'package:flutter/material.dart';
import 'screens/welcome_screen.dart';

void main() => runApp(const RakshakApp());

class RakshakApp extends StatelessWidget {
  const RakshakApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Rakshak AI',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(useMaterial3: true, colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff668d5d))),
        home: const WelcomeScreen(),
      );
}

