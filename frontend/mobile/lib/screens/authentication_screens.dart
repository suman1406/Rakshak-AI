import 'package:flutter/material.dart';
import '../api_client.dart';
import '../core/app_theme.dart';
import '../widgets/app_components.dart';
import 'dashboard_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final formKey = GlobalKey<FormState>();
  final email = TextEditingController();
  final password = TextEditingController();
  bool obscure = true;
  bool submitting = false;
  String? error;

  @override
  Widget build(BuildContext context) {
    return AppPage(
      title: 'Welcome back',
      onBack: () => Navigator.pop(context),
      child: PageContent(children: [
        const SizedBox(height: 12),
        Text('Sign in to your fields',
            style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 8),
        const Text('Use your Rakshak account to continue.'),
        const SizedBox(height: 28),
        Form(
          key: formKey,
          child: Column(children: [
            TextFormField(
                controller: email,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                    labelText: 'Email address',
                    prefixIcon: Icon(Icons.mail_outline)),
                validator: requiredField),
            const SizedBox(height: 14),
            TextFormField(
                controller: password,
                obscureText: obscure,
                decoration: InputDecoration(
                    labelText: 'Password',
                    prefixIcon: const Icon(Icons.lock_outline),
                    suffixIcon: IconButton(
                        onPressed: () => setState(() => obscure = !obscure),
                        icon: Icon(obscure
                            ? Icons.visibility_outlined
                            : Icons.visibility_off_outlined))),
                validator: requiredField),
            const SizedBox(height: 24),
            if (error != null) ...[
              AppCard(color: RakshakColors.error, child: Text(error!, style: const TextStyle(color: RakshakColors.errorText))),
              const SizedBox(height: 12),
            ],
            PrimaryAction(
                label: submitting ? 'Signing in...' : 'Sign in',
                icon: Icons.arrow_forward_rounded,
                onPressed: submitting ? null : () async {
                  if (!formKey.currentState!.validate()) return;
                  setState(() { submitting = true; error = null; });
                  try {
                    await ApiClient.instance.login(email.text.trim(), password.text);
                    if (!mounted) return;
                    navigateTo(context, const HomeScreen());
                  } catch (exception) {
                    if (mounted) setState(() => error = exception.toString());
                  } finally {
                    if (mounted) setState(() => submitting = false);
                  }
                }),
          ]),
        ),
        const SizedBox(height: 14),
        SecondaryAction(
            label: 'Create an account',
            onPressed: () => navigateTo(context, const RegisterScreen())),
        const SizedBox(height: 24),
        const SafetyNote(),
      ]),
    );
  }
}

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});
  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final formKey = GlobalKey<FormState>();
  final name = TextEditingController();
  final phone = TextEditingController();
  final email = TextEditingController();
  final password = TextEditingController();
  bool submitting = false;
  String? error;
  @override
  Widget build(BuildContext context) => AppPage(
        title: 'Create account',
        onBack: () => Navigator.pop(context),
        child: PageContent(children: [
          Text('Your fields, in one place.',
              style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 8),
          const Text('Set up a simple farmer profile for this pilot.'),
          const SizedBox(height: 24),
          Form(
              key: formKey,
              child: Column(children: [
                TextFormField(controller: name,
                    decoration: const InputDecoration(labelText: 'Full name'),
                    validator: requiredField),
                const SizedBox(height: 14),
                TextFormField(controller: phone,
                    decoration: const InputDecoration(labelText: 'Phone number'),
                    validator: requiredField),
                const SizedBox(height: 14),
                TextFormField(controller: email,
                    decoration: const InputDecoration(labelText: 'Email address'),
                    validator: requiredField),
                const SizedBox(height: 14),
                TextFormField(controller: password, obscureText: true, decoration: const InputDecoration(labelText: 'Password'), validator: requiredField),
                const SizedBox(height: 16),
                if (error != null) ...[AppCard(color: RakshakColors.error, child: Text(error!, style: const TextStyle(color: RakshakColors.errorText))), const SizedBox(height: 12)],
                PrimaryAction(
                    label: submitting ? 'Creating account...' : 'Create account',
                    onPressed: submitting ? null : () async {
                      if (!formKey.currentState!.validate()) return;
                      setState(() { submitting = true; error = null; });
                      try {
                        await ApiClient.instance.register(name: name.text.trim(), phone: phone.text.trim(), email: email.text.trim(), password: password.text);
                        await ApiClient.instance.login(email.text.trim(), password.text);
                        if (!mounted) return;
                        navigateTo(context, const HomeScreen());
                      } catch (exception) { if (mounted) setState(() => error = exception.toString()); }
                      finally { if (mounted) setState(() => submitting = false); }
                    }),
              ])),
        ]),
      );
}

String? requiredField(String? value) =>
    value == null || value.trim().isEmpty ? 'This field is required' : null;
