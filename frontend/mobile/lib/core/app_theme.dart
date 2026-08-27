import 'package:flutter/material.dart';

class RakshakColors {
  static const ink = Color(0xff14231d);
  static const canvas = Color(0xfff7faf4);
  static const leaf = Color(0xff526259);
  static const signal = Color(0xffd4ee66);
  static const border = Color(0xffdfe7dc);
  static const healthy = Color(0xffe6f0d8);
  static const warning = Color(0xffffead8);
  static const warningText = Color(0xff9b5526);
  static const error = Color(0xffffe1df);
  static const errorText = Color(0xff8d3631);
}

ThemeData buildRakshakTheme() {
  final scheme = ColorScheme.fromSeed(seedColor: RakshakColors.ink);
  return ThemeData(
    useMaterial3: true,
    scaffoldBackgroundColor: RakshakColors.canvas,
    colorScheme: scheme.copyWith(
      primary: RakshakColors.ink,
      onPrimary: Colors.white,
      secondary: RakshakColors.leaf,
      tertiary: RakshakColors.signal,
      surface: Colors.white,
      error: RakshakColors.errorText,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: RakshakColors.canvas,
      surfaceTintColor: Colors.transparent,
      foregroundColor: RakshakColors.ink,
      centerTitle: false,
      elevation: 0,
    ),
    textTheme: const TextTheme(
      displaySmall: TextStyle(
          fontSize: 36,
          height: 1.08,
          fontWeight: FontWeight.w800,
          color: RakshakColors.ink),
      headlineSmall: TextStyle(
          fontSize: 26,
          height: 1.2,
          fontWeight: FontWeight.w800,
          color: RakshakColors.ink),
      titleLarge: TextStyle(
          fontSize: 20,
          height: 1.3,
          fontWeight: FontWeight.w800,
          color: RakshakColors.ink),
      titleMedium: TextStyle(
          fontSize: 16,
          height: 1.35,
          fontWeight: FontWeight.w700,
          color: RakshakColors.ink),
      bodyLarge:
          TextStyle(fontSize: 17, height: 1.45, color: RakshakColors.leaf),
      bodyMedium:
          TextStyle(fontSize: 15, height: 1.4, color: RakshakColors.leaf),
      labelLarge: TextStyle(
          fontSize: 15, fontWeight: FontWeight.w800, color: RakshakColors.ink),
      labelMedium: TextStyle(
          fontSize: 13, fontWeight: FontWeight.w700, color: RakshakColors.leaf),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.white,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 15),
      labelStyle: const TextStyle(color: RakshakColors.leaf),
      border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: RakshakColors.border)),
      enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: RakshakColors.border)),
      focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: RakshakColors.ink, width: 2)),
      errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: RakshakColors.errorText)),
      focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide:
              const BorderSide(color: RakshakColors.errorText, width: 2)),
    ),
    filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
            minimumSize: const Size.fromHeight(52),
            backgroundColor: RakshakColors.signal,
            foregroundColor: RakshakColors.ink,
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10)))),
    outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
            minimumSize: const Size.fromHeight(52),
            foregroundColor: RakshakColors.ink,
            side: const BorderSide(color: RakshakColors.ink),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10)))),
    navigationBarTheme: NavigationBarThemeData(
        backgroundColor: Colors.white,
        indicatorColor: RakshakColors.healthy,
        labelTextStyle: WidgetStateProperty.all(const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: RakshakColors.ink))),
  );
}
