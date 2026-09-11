import 'package:flutter/material.dart';
import '../api_client.dart';
import '../widgets/app_components.dart';
import 'welcome_screen.dart';

class SecurityScreen extends StatefulWidget {
  const SecurityScreen({super.key});
  @override
  State<SecurityScreen> createState() => _SecurityState();
}

class _SecurityState extends State<SecurityScreen> {
  final current = TextEditingController();
  final password = TextEditingController();
  final confirmation = TextEditingController();
  final form = GlobalKey<FormState>();
  bool? consent;
  bool busy = false;
  String? error;
  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    try {
      final user = await ApiClient.instance.currentUser();
      if (mounted) setState(() => consent = user['training_consent'] == true);
    } catch (_) {
      if (mounted) {
        setState(() => error = 'Could not load preferences. Please try again.');
      }
    }
  }

  @override
  void dispose() {
    current.dispose();
    password.dispose();
    confirmation.dispose();
    super.dispose();
  }

  Future<void> run(Future<void> Function() action,
      {bool signOut = false}) async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await action();
      if (!mounted) return;
      if (signOut) {
        Navigator.of(context).pushAndRemoveUntil(
            MaterialPageRoute(builder: (_) => const WelcomeScreen()),
            (_) => false);
      } else {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('Preference saved')));
      }
    } catch (e) {
      if (mounted) {
        setState(() => error = e is ApiException
            ? e.message
            : 'Could not save changes. Please try again.');
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => AppPage(
      title: 'Security & consent',
      onBack: () => Navigator.pop(context),
      child: PageContent(children: [
        if (error != null) AppCard(child: Text(error!)),
        Text('Optional model training',
            style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        const Text(
            'Allow evidence and expert corrections in future training exports. This is optional and does not affect scan processing. Withdrawing consent stops future exports.'),
        SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Allow model-training use'),
            value: consent == true,
            onChanged: consent == null || busy
                ? null
                : (value) => run(() async {
                      await ApiClient.instance
                          .updateProfile({'training_consent': value});
                      if (mounted) setState(() => consent = value);
                    })),
        if (consent == null)
          SecondaryAction(
              label: 'Reload preferences', onPressed: busy ? null : load),
        const SizedBox(height: 24),
        Text('Change password', style: Theme.of(context).textTheme.titleLarge),
        Form(
            key: form,
            child: Column(children: [
              TextFormField(
                  controller: current,
                  obscureText: true,
                  autofillHints: const [AutofillHints.password],
                  decoration:
                      const InputDecoration(labelText: 'Current password'),
                  validator: (value) => value == null || value.isEmpty
                      ? 'Enter your current password'
                      : null),
              TextFormField(
                  controller: password,
                  obscureText: true,
                  autofillHints: const [AutofillHints.newPassword],
                  decoration: const InputDecoration(labelText: 'New password'),
                  validator: (value) => value == null || value.length < 8
                      ? 'Use at least 8 characters'
                      : null),
              TextFormField(
                  controller: confirmation,
                  obscureText: true,
                  decoration:
                      const InputDecoration(labelText: 'Repeat new password'),
                  validator: (value) =>
                      value != password.text ? 'Passwords do not match' : null),
            ])),
        const SizedBox(height: 16),
        const Text('Changing your password signs you out on all devices.'),
        const SizedBox(height: 16),
        PrimaryAction(
            label: busy ? 'Saving…' : 'Change password & sign out',
            onPressed: busy
                ? null
                : () {
                    if (form.currentState!.validate()) {
                      run(
                          () => ApiClient.instance
                              .changePassword(current.text, password.text),
                          signOut: true);
                    }
                  }),
        const SizedBox(height: 24),
        SecondaryAction(
            label: 'Sign out on every device',
            onPressed: busy
                ? null
                : () =>
                    run(() => ApiClient.instance.logoutAll(), signOut: true)),
      ]));
}
