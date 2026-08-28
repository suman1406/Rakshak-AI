import 'package:flutter/material.dart';
import '../api_client.dart';
import '../core/app_theme.dart';
import '../widgets/app_components.dart';
import 'feedback_screens.dart';
import 'scan_screens.dart';

class CropHealthReportScreen extends StatefulWidget {
  const CropHealthReportScreen({super.key, this.videoId});
  final String? videoId;
  @override State<CropHealthReportScreen> createState() => _ReportState();
}

class _ReportState extends State<CropHealthReportScreen> {
  Future<Map<String, dynamic>>? analysis;
  Future<List<Map<String, dynamic>>>? frames;
  @override void initState() { super.initState(); _load(); }
  void _load() { if (widget.videoId != null) { analysis = ApiClient.instance.videoAnalysis(widget.videoId!); frames = ApiClient.instance.evidenceFrames(widget.videoId!); } }
  @override Widget build(BuildContext context) {
    if (analysis == null) return _report(context, null, const []);
    return FutureBuilder<Map<String, dynamic>>(future: analysis, builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) return const Scaffold(body: Center(child: CircularProgressIndicator()));
      if (snapshot.hasError) return AppPage(title: 'Crop health report', onBack: () => Navigator.pop(context), child: PageContent(children: [const AppCard(child: Text('This report is temporarily unavailable.')), PrimaryAction(label: 'Try again', onPressed: () => setState(_load))]));
      return FutureBuilder<List<Map<String, dynamic>>>(future: frames, builder: (context, frameSnapshot) => _report(context, snapshot.data, frameSnapshot.data ?? const []));
    });
  }
  Widget _report(BuildContext context, Map<String, dynamic>? data, List<Map<String, dynamic>> frameData) {
    final diagnosis = (data?['diagnosis'] as Map?)?.cast<String, dynamic>() ?? {};
    final evidence = (data?['evidence'] as Map?)?.cast<String, dynamic>() ?? {};
    final disease = diagnosis['disease']?.toString() ?? 'Soybean health signal';
    final confidence = ((diagnosis['confidence'] as num?)?.toDouble() ?? 0) * 100;
    final diagnosisId = data?['diagnosis_id']?.toString();
    return AppPage(title: 'Crop health report', onBack: () => Navigator.pop(context), child: PageContent(children: [
      AppCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Row(children: [Expanded(child: Text(disease, style: Theme.of(context).textTheme.headlineSmall)), const StatusBadge(label: 'AI indication', color: RakshakColors.warning, textColor: RakshakColors.warningText)]), const SizedBox(height: 8), Text(data == null ? 'North plot · Today' : 'Review recommended'), const SizedBox(height: 20), Text('${confidence.round()}%', style: Theme.of(context).textTheme.displaySmall), Text('Confidence across ${evidence['supporting_frames'] ?? 0} supporting frames')])),
      const SizedBox(height: 24), const SectionHeading(title: 'What we saw'), const SizedBox(height: 8), AppCard(child: Text(data == null ? 'A similar signal appeared across multiple leaves. This is an indication for review, not a confirmed diagnosis.' : 'The signal was aggregated across multiple frames. Treat it as decision support, not a confirmed diagnosis.')),
      const SizedBox(height: 24), SectionHeading(title: 'Evidence frames', actionLabel: '${frameData.length} frames'), const SizedBox(height: 8), SizedBox(height: 104, child: frameData.isEmpty ? const AppCard(child: Text('Evidence frames will appear when the API provides them.')) : ListView.separated(scrollDirection: Axis.horizontal, itemCount: frameData.length, separatorBuilder: (_, __) => const SizedBox(width: 10), itemBuilder: (_, i) => Container(width: 128, decoration: BoxDecoration(color: RakshakColors.border, borderRadius: BorderRadius.circular(12)), child: Center(child: Text('Frame ${(frameData[i]['sequence_index'] ?? i + 1)}'))))),
      const SizedBox(height: 24), const AppCard(child: Text('Suggested next step\n\nReview the evidence with an agronomist before taking treatment action.')), const SizedBox(height: 24), PrimaryAction(label: 'Share feedback', onPressed: diagnosisId == null ? null : () => navigateTo(context, FeedbackScreen(diagnosisId: diagnosisId))), const SizedBox(height: 10), SecondaryAction(label: 'Scan another area', onPressed: () => navigateTo(context, const NewScanScreen())), const SafetyNote()
    ]));
  }
}

class HealthyCropScreen extends StatelessWidget { const HealthyCropScreen({super.key}); @override Widget build(BuildContext context) => const ResultStateScreen(title: 'Healthy crop', icon: Icons.check_circle_outline, statusColor: RakshakColors.healthy, description: 'No significant disease signal was detected in this scan.', detail: 'Your soybean leaves look consistent across the reviewed frames.', action: 'Scan another area'); }
class UncertainResultScreen extends StatelessWidget { const UncertainResultScreen({super.key}); @override Widget build(BuildContext context) => const ResultStateScreen(title: 'Needs a closer look', icon: Icons.help_outline, statusColor: RakshakColors.warning, description: 'The signal is not strong enough for a reliable result.', detail: 'Try a steadier video in better light, or ask an agronomist to review the evidence frames.', action: 'Request review'); }
class ResultStateScreen extends StatelessWidget { const ResultStateScreen({super.key, required this.title, required this.icon, required this.statusColor, required this.description, required this.detail, required this.action}); final String title, description, detail, action; final IconData icon; final Color statusColor; @override Widget build(BuildContext context) => AppPage(title: 'Crop health report', onBack: () => Navigator.pop(context), child: PageContent(crossAxisAlignment: CrossAxisAlignment.center, children: [const SizedBox(height: 42), Container(width: 96, height: 96, decoration: BoxDecoration(color: statusColor, shape: BoxShape.circle), child: Icon(icon, size: 48, color: RakshakColors.ink)), const SizedBox(height: 22), Text(title, textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 12), Text(description, textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodyLarge), const SizedBox(height: 24), AppCard(child: Text(detail, style: Theme.of(context).textTheme.bodyMedium)), const SizedBox(height: 24), PrimaryAction(label: action, onPressed: () => navigateTo(context, const NewScanScreen())), const SizedBox(height: 10), const SafetyNote()])); }
