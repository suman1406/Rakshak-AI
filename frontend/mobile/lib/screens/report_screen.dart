import 'package:flutter/material.dart';

class ReportScreen extends StatelessWidget { const ReportScreen({super.key});
  @override Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('Crop health')), body: ListView(padding: const EdgeInsets.all(24), children: [
    Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(color: const Color(0xffe6f0d8), borderRadius: BorderRadius.circular(18)), child: const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('POSSIBLE DISEASE', style: TextStyle(fontSize: 11, letterSpacing: 1.2)), SizedBox(height: 10), Text('Soybean rust', style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold)), SizedBox(height: 8), Text('Confidence: Medium  •  Severity: Moderate') ])), const SizedBox(height: 22),
    const Text('What we found', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)), const SizedBox(height: 8), const Text('Similar leaf symptoms were detected across multiple plants in your video. This is an AI indication, not a confirmed diagnosis.', style: TextStyle(color: Color(0xff66766d), height: 1.5)), const SizedBox(height: 24),
    const ListTile(leading: Icon(Icons.photo_library_outlined), title: Text('12 supporting frames'), subtitle: Text('43 leaf regions analyzed')), const ListTile(leading: Icon(Icons.task_alt), title: Text('What to do now'), subtitle: Text('Inspect more plants, capture close-ups, and consult an agronomist if symptoms spread.')),
    FilledButton(onPressed: () {}, child: const Text('Send for agronomist review')),
  ])); }
}

