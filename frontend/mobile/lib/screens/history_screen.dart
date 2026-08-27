import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../demo_data.dart';
import '../widgets/app_components.dart';
import 'report_screens.dart';

class ScanHistoryScreen extends StatelessWidget {
  const ScanHistoryScreen({super.key});
  @override
  Widget build(BuildContext context) => PageContent(children: [
        Text('Scan history', style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 8),
        const Text('Your field observations and reports.'),
        const SizedBox(height: 22),
        for (final scan in demoScans)
          Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: InkWell(
                  onTap: () =>
                      navigateTo(context, const CropHealthReportScreen()),
                  child: AppCard(
                      child: Row(children: [
                    const Icon(Icons.analytics_outlined,
                        color: RakshakColors.leaf),
                    const SizedBox(width: 12),
                    Expanded(
                        child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                          Text(scan.disease,
                              style:
                                  const TextStyle(fontWeight: FontWeight.w800)),
                          Text('${scan.field} · ${scan.date}'),
                          Text(
                              '${scan.severity} · ${scan.confidence}% confidence')
                        ]))
                  ])))),
        const SizedBox(height: 12),
        const EmptyState(
            icon: Icons.add_a_photo_outlined,
            title: 'Keep observing',
            body:
                'Start another scan when you visit a different area of the field.')
      ]);
}
