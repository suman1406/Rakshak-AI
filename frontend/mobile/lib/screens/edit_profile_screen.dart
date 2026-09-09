import 'package:flutter/material.dart';
import '../api_client.dart';
import '../widgets/app_components.dart';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key, required this.name});
  final String name;
  @override State<EditProfileScreen> createState() => _EditProfileState();
}
class _EditProfileState extends State<EditProfileScreen> {
  late final TextEditingController name;
  final form = GlobalKey<FormState>();
  bool saving = false;
  String? error;
  @override void initState() { super.initState(); name = TextEditingController(text: widget.name); }
  @override void dispose() { name.dispose(); super.dispose(); }
  Future<void> save() async {
    if (!form.currentState!.validate()) return;
    setState(() { saving = true; error = null; });
    try { await ApiClient.instance.updateProfile({'display_name': name.text.trim()}); if (mounted) Navigator.pop(context, true); }
    catch (_) { if (mounted) setState(() { saving = false; error = 'Could not save your name. Please try again.'; }); }
  }
  @override Widget build(BuildContext context) => AppPage(title: 'Edit profile', onBack: () => Navigator.pop(context), child: PageContent(children: [
    Form(key: form, child: TextFormField(controller: name, decoration: const InputDecoration(labelText: 'Your name'), maxLength: 255, validator: (value) => value == null || value.trim().isEmpty ? 'Enter your name' : null)),
    if (error != null) Text(error!), const SizedBox(height: 24), PrimaryAction(label: saving ? 'Saving…' : 'Save profile', onPressed: saving ? null : save),
  ]));
}
