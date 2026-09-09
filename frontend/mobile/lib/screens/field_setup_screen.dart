import 'package:flutter/material.dart';
import '../api_client.dart';
import '../widgets/app_components.dart';

class FieldSetupScreen extends StatefulWidget {
  const FieldSetupScreen({super.key});
  @override
  State<FieldSetupScreen> createState() => _FieldSetupState();
}

class _FieldSetupState extends State<FieldSetupScreen> {
  final form = GlobalKey<FormState>();
  final farmName = TextEditingController();
  final fieldName = TextEditingController();
  final area = TextEditingController();
  List<Map<String, dynamic>> farms = [];
  String? farmId;
  String? error;
  bool loading = true, saving = false;

  @override
  void initState() {
    super.initState();
    load();
  }

  @override
  void dispose() {
    farmName.dispose();
    fieldName.dispose();
    area.dispose();
    super.dispose();
  }

  Future<void> load() async {
    try {
      final result = await ApiClient.instance.listFarms();
      if (mounted) {
        setState(() {
          farms = result;
          farmId = result.isEmpty ? null : result.first['id'].toString();
          loading = false;
          error = null;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          loading = false;
          error =
              'Could not load your farms. Check your connection and try again.';
        });
      }
    }
  }

  Future<void> save() async {
    if (!form.currentState!.validate() || saving) return;
    setState(() {
      saving = true;
      error = null;
    });
    try {
      if (farmId == null) {
        final farm = await ApiClient.instance.createFarm(farmName.text.trim());
        farmId = farm['id'].toString();
        farms.add(farm);
      }
      await ApiClient.instance.createField(
          farmId!, fieldName.text.trim(), double.tryParse(area.text));
      if (mounted) Navigator.pop(context, true);
    } catch (_) {
      if (mounted) {
        setState(() {
          saving = false;
          error =
              'Your field could not be saved. Your entries are still here; please try again.';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) => AppPage(
        title: 'Add a field',
        onBack: () => Navigator.pop(context),
        child: loading
            ? const Center(child: CircularProgressIndicator())
            : PageContent(children: [
                Text('Keep every scan with its field',
                    style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: 12),
                const Text(
                    'Give your field a familiar name. Soybean is the supported crop for this release.'),
                const SizedBox(height: 24),
                if (error != null) ...[
                  Text(error!),
                  TextButton(onPressed: load, child: const Text('Reload farms'))
                ],
                Form(
                    key: form,
                    child: Column(children: [
                      if (farms.isNotEmpty) ...[
                        DropdownButtonFormField<String>(
                            initialValue: farmId ?? '',
                            decoration:
                                const InputDecoration(labelText: 'Farm'),
                            items: [
                              ...farms.map((farm) => DropdownMenuItem(
                                  value: farm['id'].toString(),
                                  child: Text(farm['name'].toString()))),
                              const DropdownMenuItem(
                                  value: '', child: Text('Create a new farm')),
                            ],
                            onChanged: saving
                                ? null
                                : (value) => setState(
                                    () => farmId = value == '' ? null : value)),
                        const SizedBox(height: 16),
                      ],
                      if (farmId == null) ...[
                        TextFormField(
                            controller: farmName,
                            decoration:
                                const InputDecoration(labelText: 'Farm name'),
                            maxLength: 255,
                            validator: (v) => v == null || v.trim().isEmpty
                                ? 'Enter a farm name'
                                : null),
                        const SizedBox(height: 16)
                      ],
                      TextFormField(
                          controller: fieldName,
                          decoration: const InputDecoration(
                              labelText: 'Field name',
                              hintText: 'East soybean field'),
                          maxLength: 255,
                          validator: (v) => v == null || v.trim().isEmpty
                              ? 'Enter a field name'
                              : null),
                      const SizedBox(height: 16),
                      TextFormField(
                          controller: area,
                          keyboardType: const TextInputType.numberWithOptions(
                              decimal: true),
                          decoration: const InputDecoration(
                              labelText: 'Area in hectares (optional)'),
                          validator: (v) => v != null &&
                                  v.isNotEmpty &&
                                  (double.tryParse(v) == null ||
                                      !double.parse(v).isFinite ||
                                      double.parse(v) <= 0)
                              ? 'Enter a positive area'
                              : null),
                      const SizedBox(height: 24),
                      PrimaryAction(
                          label: saving ? 'Saving field…' : 'Save field',
                          onPressed: saving ? null : save),
                    ])),
              ]),
      );
}
