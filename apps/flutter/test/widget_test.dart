import 'package:flutter_test/flutter_test.dart';
import 'package:adf_flutter_reference/main.dart';
void main(){testWidgets('statut présent',(tester) async {await tester.pumpWidget(const AdfApp());expect(find.text('Prêt'),findsOneWidget);});}
