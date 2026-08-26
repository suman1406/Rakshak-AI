import 'package:flutter/material.dart';
import '../demo_data.dart';
import 'report_screen.dart';
import 'scan_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});
  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Rakshak AI'), actions: [IconButton(onPressed: () {}, icon: const Icon(Icons.notifications_none))]),
        body: ListView(padding: const EdgeInsets.fromLTRB(20, 8, 20, 28), children: [
          const Text('Good morning, farmer.', style: TextStyle(color: Color(0xff66766d))),
          const SizedBox(height: 6),
          const Text('Your fields at a glance.', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, letterSpacing: -1)),
          const SizedBox(height: 22),
          Row(children: [Expanded(child: _Metric(label: 'Fields', value: '${demoFields.length}')), const SizedBox(width: 12), Expanded(child: _Metric(label: 'Avg health', value: '82'))]),
          const SizedBox(height: 24),
          FilledButton.icon(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ScanScreen())), icon: const Icon(Icons.add_a_photo_outlined), label: const Text('Start a new scan')),
          const SizedBox(height: 28),
          const Text('Your fields', style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          ...demoFields.map((field) => Card(margin: const EdgeInsets.only(bottom: 10), child: ListTile(leading: CircleAvatar(backgroundColor: const Color(0xffe6f0d8), child: Text('${field.health}', style: const TextStyle(color: Color(0xff315f3a), fontWeight: FontWeight.bold))), title: Text(field.name), subtitle: Text('${field.crop}  •  ${field.status}'), trailing: const Icon(Icons.chevron_right)))),
          const SizedBox(height: 18),
          const Text('Recent scans', style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          ...demoScans.map((scan) => ListTile(contentPadding: EdgeInsets.zero, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ReportScreen())), leading: const Icon(Icons.eco_outlined), title: Text(scan.disease), subtitle: Text('${scan.field}  •  ${scan.date}'), trailing: Text('${scan.confidence}%'))),
        ],
      );
}

class _Metric extends StatelessWidget {
  const _Metric({required this.label, required this.value});
  final String label;
  final String value;
  @override
  Widget build(BuildContext context) => Container(padding: const EdgeInsets.all(18), decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0xffdfe7dc))), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(label, style: const TextStyle(color: Color(0xff66766d), fontSize: 12)), const SizedBox(height: 8), Text(value, style: const TextStyle(fontSize: 30, fontWeight: FontWeight.bold))]));
}

