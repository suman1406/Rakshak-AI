import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../api_client.dart';
import '../widgets/app_components.dart';
import 'report_screens.dart';

class ScanHistoryScreen extends StatefulWidget {
  const ScanHistoryScreen({super.key});
  @override State<ScanHistoryScreen> createState() => _ScanHistoryScreenState();
}

class _ScanHistoryScreenState extends State<ScanHistoryScreen> {
  late Future<List<Map<String, dynamic>>> scans;
  @override void initState() { super.initState(); scans = ApiClient.instance.listVideos(); }
  @override
  Widget build(BuildContext context) => FutureBuilder<List<Map<String, dynamic>>>(future: scans, builder: (context, snapshot) => PageContent(children: [
        Text('Scan history', style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 8),
        const Text('Your field observations and reports.'),
        const SizedBox(height: 22),
        if (snapshot.connectionState == ConnectionState.waiting) const Center(child: CircularProgressIndicator()),
        if (snapshot.hasError) const AppCard(child: Text('Could not load scan history. Please try again.')),
        for (final scan in snapshot.data ?? const <Map<String, dynamic>>[])
          Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: InkWell(
                  onTap: () =>
                      navigateTo(context, CropHealthReportScreen(videoId: scan['video_id']?.toString())),
                  child: AppCard(
                      child: Row(children: [
                    const Icon(Icons.analytics_outlined,
                        color: RakshakColors.leaf),
                    const SizedBox(width: 12),
                    Expanded(
                        child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                          Text(scan['status']?.toString() ?? 'Scan',
                              style:
                                  const TextStyle(fontWeight: FontWeight.w800)),
                          const Text('Field observation'),
                          Text(scan['status']?.toString() == 'failed' ? 'This scan could not be completed. Open it for next steps.' : 'Open report for details')
                        ]))
                  ])))),
        const SizedBox(height: 12),
        if (snapshot.hasData && snapshot.data!.isEmpty) const EmptyState(
            icon: Icons.add_a_photo_outlined,
            title: 'Keep observing',
            body:
                'Start another scan when you visit a different area of the field.')
      ]));
}
