import 'package:flutter_test/flutter_test.dart';
import 'package:rakshak_mobile/main.dart';

void main() { testWidgets('shows onboarding content', (tester) async { await tester.pumpWidget(const RakshakApp()); expect(find.text('See what your crop is telling you.'), findsOneWidget); }); }

