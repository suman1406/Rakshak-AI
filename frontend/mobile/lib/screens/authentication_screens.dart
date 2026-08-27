import 'package:flutter/material.dart';
import '../widgets/app_components.dart';
import 'dashboard_screen.dart';
import 'onboarding_screens.dart';

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
            PrimaryAction(
                label: 'Sign in',
                icon: Icons.arrow_forward_rounded,
                onPressed: () {
                  if (formKey.currentState!.validate())
                    navigateTo(context, const HomeScreen());
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
                const TextFormField(
                    decoration: InputDecoration(labelText: 'Full name'),
                    validator: requiredField),
                const SizedBox(height: 14),
                const TextFormField(
                    decoration: InputDecoration(labelText: 'Phone number'),
                    validator: requiredField),
                const SizedBox(height: 14),
                const TextFormField(
                    decoration: InputDecoration(labelText: 'Email address'),
                    validator: requiredField),
                const SizedBox(height: 24),
                PrimaryAction(
                    label: 'Continue',
                    onPressed: () {
                      if (formKey.currentState!.validate())
                        navigateTo(context, const OnboardingScreen());
                    }),
              ])),
        ]),
      );
}

String? requiredField(String? value) =>
    value == null || value.trim().isEmpty ? 'This field is required' : null;
