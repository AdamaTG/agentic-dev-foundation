import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:adf_flutter_reference/main.dart';
void main(){IntegrationTestWidgetsFlutterBinding.ensureInitialized();testWidgets('écran de référence',(tester) async {await tester.pumpWidget(const AdfApp());expect(find.text('ADF Flutter Reference'),findsOneWidget);});}
