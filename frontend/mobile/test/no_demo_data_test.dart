import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

void main() {
  test('mobile application has no demo-data source or demo imports', () {
    expect(File('lib/demo_data.dart').existsSync(), isFalse);
    final files = Directory('lib').listSync(recursive: true).whereType<File>().where((file) => file.path.endsWith('.dart'));
    final violations = <String>[];
    for (final file in files) {
      final content = file.readAsStringSync();
      for (final term in ['demo_data.dart', 'DemoField', 'DemoScan', 'demoFields', 'demoScans']) {
        if (content.contains(term)) violations.add('${file.path}: $term');
      }
    }
    expect(violations, isEmpty);
  });
}
