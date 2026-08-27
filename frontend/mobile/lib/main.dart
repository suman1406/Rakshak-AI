import 'package:flutter/material.dart';
import 'screens/stitch_screens.dart';

void main() => runApp(const RakshakApp());

class RakshakApp extends StatelessWidget {
  const RakshakApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Rakshak AI',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
            useMaterial3: true,
            scaffoldBackgroundColor: const Color(0xfff7faf4),
            colorScheme:
                ColorScheme.fromSeed(seedColor: const Color(0xff14231d))
                    .copyWith(
                        primary: const Color(0xff14231d),
                        tertiary: const Color(0xffd4ee66)),
            inputDecorationTheme: InputDecorationTheme(
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: const BorderSide(color: Color(0xffdfe7dc))),
                enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: const BorderSide(color: Color(0xffdfe7dc))),
                focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide:
                        const BorderSide(color: Color(0xff14231d), width: 2)),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 15))),
        home: const WelcomeScreen(),
      );
}
