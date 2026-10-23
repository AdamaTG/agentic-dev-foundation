// Copy to apps/flutter/integration_test/app_test.dart and adjust app import.
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:your_app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('home screen renders', (tester) async {
    app.main();
    await tester.pumpAndSettle();
    expect(find.text('Home'), findsOneWidget);
  });
}
