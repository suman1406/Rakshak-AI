import 'package:flutter/material.dart';
import 'scan_screen.dart';

class LoginScreen extends StatefulWidget { const LoginScreen({super.key}); @override State<LoginScreen> createState() => _LoginScreenState(); }
class _LoginScreenState extends State<LoginScreen> {
  final email = TextEditingController(); final password = TextEditingController();
  @override Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('Sign in')), body: ListView(padding: const EdgeInsets.all(24), children: [
    const Text('Your field view awaits.', style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold)), const SizedBox(height: 30),
    TextField(controller: email, decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder())), const SizedBox(height: 16),
    TextField(controller: password, obscureText: true, decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder())), const SizedBox(height: 24),
    FilledButton(onPressed: () => Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const ScanScreen())), child: const Text('Continue')),
  ]));
}

