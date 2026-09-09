import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rakshak_mobile/core/app_theme.dart';
import 'package:rakshak_mobile/screens/authentication_screens.dart';

void main() {
  test('password validation handles UTF-8 length used by password hashing', () {
    expect(validateNewPassword('short'), isNotNull);
    expect(validateNewPassword('ValidPassword123!'), isNull);
    expect(validateNewPassword(List.filled(30, '🌱').join()), isNotNull);
  });

  testWidgets('sign-in validation works on a narrow screen with large text',
      (tester) async {
    tester.view.physicalSize = const Size(360, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(MaterialApp(
        theme: buildRakshakTheme(),
        builder: (context, child) => MediaQuery(
            data: MediaQuery.of(context)
                .copyWith(textScaler: const TextScaler.linear(1.5)),
            child: child!),
        home: const LoginScreen()));
    await tester.ensureVisible(find.text('Sign in'));
    await tester.tap(find.text('Sign in'));
    await tester.pumpAndSettle();
    expect(find.text('This field is required'), findsNWidgets(2));
    expect(tester.takeException(), isNull);
  });

  testWidgets('registration rejects missing consent before making a request',
      (tester) async {
    await tester.pumpWidget(
        MaterialApp(theme: buildRakshakTheme(), home: const RegisterScreen()));
    await tester
        .ensureVisible(find.widgetWithText(FilledButton, 'Create account'));
    await tester.tap(find.widgetWithText(FilledButton, 'Create account'));
    await tester.pumpAndSettle();
    expect(
        find.text(
            'Please agree to data processing before creating an account.'),
        findsOneWidget);
    expect(find.text('Use at least 8 characters'), findsWidgets);
    expect(tester.takeException(), isNull);
  });
}
