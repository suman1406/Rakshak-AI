import 'package:flutter_test/flutter_test.dart';
import 'package:rakshak_mobile/main.dart';

void main() {
  testWidgets('shows the Rakshak welcome screen', (tester) async {
    await tester.pumpWidget(const RakshakApp());
    expect(find.text('See your crop\nwith more clarity.'), findsOneWidget);
  });
}
