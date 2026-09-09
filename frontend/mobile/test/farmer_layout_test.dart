import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:rakshak_mobile/core/app_theme.dart';
import 'package:rakshak_mobile/screens/welcome_screen.dart';

void main() {
  testWidgets('farmer welcome remains usable at narrow width and large text',
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
        home: const WelcomeScreen()));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Create your farmer account'));
    await tester.tap(find.text('Create your farmer account'));
    await tester.pumpAndSettle();
    expect(find.widgetWithText(FilledButton, 'Create account'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('render farmer welcome for visual inspection when requested',
      (tester) async {
    final output = Platform.environment['RAKSHAK_VISUAL_OUTPUT'];
    if (output == null) return;
    final sdk = Platform.environment['FLUTTER_ROOT'];
    if (sdk != null) {
      await tester.runAsync(() async {
        final loader = FontLoader('Roboto');
        loader.addFont(
            File('$sdk/bin/cache/artifacts/material_fonts/roboto-regular.ttf')
                .readAsBytes()
                .then((b) => ByteData.sublistView(b)));
        await loader.load();
        final icons = FontLoader('MaterialIcons');
        icons.addFont(File(
                '$sdk/bin/cache/artifacts/material_fonts/materialicons-regular.otf')
            .readAsBytes()
            .then((b) => ByteData.sublistView(b)));
        await icons.load();
      });
    }
    tester.view.physicalSize = const Size(390, 940);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final key = GlobalKey();
    await tester.pumpWidget(RepaintBoundary(
        key: key,
        child: MaterialApp(
            debugShowCheckedModeBanner: false,
            theme: buildRakshakTheme(),
            home: const WelcomeScreen())));
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    final boundary =
        key.currentContext!.findRenderObject()! as RenderRepaintBoundary;
    await tester.runAsync(() async {
      final image = await boundary.toImage();
      final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
      await File(output).writeAsBytes(bytes!.buffer.asUint8List());
      image.dispose();
    });
  });
}
