import 'package:flutter/material.dart';
import '../api_client.dart';
import '../widgets/app_components.dart';

class SupportScreen extends StatefulWidget {
  const SupportScreen({super.key});
  @override
  State<SupportScreen> createState() => _SupportState();
}

class _SupportState extends State<SupportScreen> {
  final form = GlobalKey<FormState>();
  final name = TextEditingController();
  final email = TextEditingController();
  final message = TextEditingController();
  bool consent = false, busy = false;
  String? error, reference;
  @override
  void dispose() {
    name.dispose();
    email.dispose();
    message.dispose();
    super.dispose();
  }

  Future<void> submit() async {
    if (!form.currentState!.validate() || !consent) return;
    setState(() {
      busy = true;
      error = null;
    });
    try {
      final result = await ApiClient.instance.contact(
          name: name.text.trim(),
          email: email.text.trim(),
          message: message.text.trim(),
          consent: consent);
      if (mounted) setState(() => reference = result['reference'].toString());
    } catch (e) {
      if (mounted) {
        setState(() => error = safeErrorMessage(e,
            fallback: 'Could not save your request. Please try again.'));
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => AppPage(
      title: 'Help & privacy requests',
      onBack: () => Navigator.pop(context),
      child: PageContent(children: [
        if (reference != null) ...[
          const Icon(Icons.check_circle_outline, size: 42),
          const Text('Your request is saved.'),
          SelectableText(reference!),
          const Text(
              'Keep this reference. The team will review your request in its inbox; no automatic email confirmation is sent.'),
        ] else
          Form(
              key: form,
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                        'Ask for help with a scan, account access, data access or deletion. Avoid sharing passwords.'),
                    const SizedBox(height: 20),
                    TextFormField(
                        controller: name,
                        maxLength: 255,
                        decoration:
                            const InputDecoration(labelText: 'Your name'),
                        validator: (v) => v == null || v.trim().isEmpty
                            ? 'Enter your name'
                            : null),
                    const SizedBox(height: 12),
                    TextFormField(
                        controller: email,
                        maxLength: 320,
                        keyboardType: TextInputType.emailAddress,
                        autofillHints: const [AutofillHints.email],
                        decoration:
                            const InputDecoration(labelText: 'Email address'),
                        validator: (v) => v == null || !v.contains('@')
                            ? 'Enter an email address'
                            : null),
                    const SizedBox(height: 12),
                    TextFormField(
                        controller: message,
                        minLines: 4,
                        maxLines: 8,
                        maxLength: 5000,
                        decoration: const InputDecoration(
                            labelText: 'How can we help?'),
                        validator: (v) => (v?.trim().length ?? 0) < 10
                            ? 'Use at least 10 characters'
                            : null),
                    CheckboxListTile(
                        contentPadding: EdgeInsets.zero,
                        value: consent,
                        onChanged: busy
                            ? null
                            : (v) => setState(() => consent = v ?? false),
                        title: const Text(
                            'I agree to using these details to handle this request.')),
                    if (error != null) Text(error!),
                    PrimaryAction(
                        label: busy ? 'Saving request…' : 'Submit request',
                        onPressed: busy || !consent ? null : submit),
                  ])),
      ]));
}

class PrivacyTermsScreen extends StatelessWidget {
  const PrivacyTermsScreen({super.key});
  @override
  Widget build(BuildContext context) => AppPage(
      title: 'Privacy & terms',
      onBack: () => Navigator.pop(context),
      child: PageContent(children: [
        Text('Your records, handled carefully.',
            style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 16),
        const Text(
            'Updated 9 September 2026. We store account details, fields, uploaded videos, extracted observations, model assessments and expert reviews to operate Rakshak. Your role and organization control access. A review request makes that scan available to an authorized agronomist.'),
        const SizedBox(height: 16),
        const Text(
            'Video processing requires consent. Optional model-training permission defaults off and can be changed in Security & consent. Withdrawal excludes future exports; earlier exports require a separate request.'),
        const SizedBox(height: 16),
        const Text(
            'Evidence retention defaults to 180 days, configurable by the operator. Cleanup removes eligible video and frame media. Reports, labels, accounts and audit history remain. Backups have operator-managed retention. An optional explanation provider may receive structured assessment details, not the video.'),
        const SizedBox(height: 16),
        const Text(
            'Use only evidence you are authorized to share. Avoid people and personal documents. This soybean pilot provides preliminary visual indications, not confirmed diagnoses or pesticide prescriptions. Processing may fail or be delayed. Keep your credentials private.'),
        const SizedBox(height: 20),
        SecondaryAction(
            label: 'Request data access or deletion',
            onPressed: () => navigateTo(context, const SupportScreen())),
      ]));
}
