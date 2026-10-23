import 'package:flutter/material.dart';
void main() => runApp(const AdfApp());
class AdfApp extends StatelessWidget {
 const AdfApp({super.key});
 @override Widget build(BuildContext context) => MaterialApp(home: Scaffold(appBar: AppBar(title: const Text('ADF Flutter Reference')),body: const Center(child: Text('Prêt', key: Key('status')))));
}
