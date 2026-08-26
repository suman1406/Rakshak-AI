import 'package:flutter/material.dart';
import 'report_screen.dart';

class ScanScreen extends StatelessWidget { const ScanScreen({super.key});
  @override Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('New field scan')), body: ListView(padding: const EdgeInsets.all(24), children: [
    const Text('Start with one area.', style: TextStyle(fontSize: 30, fontWeight: FontWeight.bold)), const SizedBox(height: 12),
    const Text('Select soybean, choose a field, then upload a 10 to 30 second video. Walk slowly and keep the camera close to the leaves.', style: TextStyle(color: Color(0xff66766d), height: 1.5)), const SizedBox(height: 28),
    DropdownButtonFormField<String>(value: 'Soybean', items: const [DropdownMenuItem(value: 'Soybean', child: Text('Soybean'))], onChanged: (_) {}, decoration: const InputDecoration(labelText: 'Crop', border: OutlineInputBorder())), const SizedBox(height: 16),
    DropdownButtonFormField<String>(value: 'North plot', items: const [DropdownMenuItem(value: 'North plot', child: Text('North plot'))], onChanged: (_) {}, decoration: const InputDecoration(labelText: 'Field', border: OutlineInputBorder())), const SizedBox(height: 28),
    FilledButton.icon(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ReportScreen())), icon: const Icon(Icons.video_library_outlined), label: const Text('Choose video')), const SizedBox(height: 12),
    OutlinedButton.icon(onPressed: () {}, icon: const Icon(Icons.videocam_outlined), label: const Text('Record video')),
  ])); }
}

