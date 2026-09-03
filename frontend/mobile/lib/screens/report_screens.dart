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
    if (analysis == null) return AppPage(title: 'Crop health report', onBack: () => Navigator.pop(context), child: const PageContent(children: [AppCard(child: Text('A video identifier is required to load a real report.'))]));
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
    final state = data?['result_state']?.toString();
    if (state == 'insufficient_evidence' || state == 'failed') return ResultStateScreen(title: state == 'failed' ? 'Scan could not complete' : 'Video needs another try', icon: Icons.videocam_off_outlined, statusColor: RakshakColors.warning, description: data?['retake_guidance']?.toString() ?? 'Please capture another video.', detail: 'No diagnosis was created for this scan.', action: 'Scan another area');
    if (state == 'unknown' || state == 'unknown_other') return UncertainResultScreen(diagnosisId: diagnosisId);
    return AppPage(title: 'Crop health report', onBack: () => Navigator.pop(context), child: PageContent(children: [
      AppCard(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Row(children: [Expanded(child: Text(disease, style: Theme.of(context).textTheme.headlineSmall)), const StatusBadge(label: 'AI indication', color: RakshakColors.warning, textColor: RakshakColors.warningText)]), const SizedBox(height: 8), const Text('Decision support only — not a confirmed diagnosis.'), const SizedBox(height: 20), Text('${confidence.round()}%', style: Theme.of(context).textTheme.displaySmall), Text('Confidence across ${evidence['supporting_frames'] ?? 0} supporting frames')])),
      const SizedBox(height: 24), const SectionHeading(title: 'What we saw'), const SizedBox(height: 8), AppCard(child: Text(data?['explanation']?.toString() ?? 'No explanation was returned for this analysis.')),
      const SizedBox(height: 24), SectionHeading(title: 'Evidence frames', actionLabel: '${frameData.length} frames'), const SizedBox(height: 8), SizedBox(height: 104, child: frameData.isEmpty ? const AppCard(child: Text('Evidence frames will appear when the API provides them.')) : ListView.separated(scrollDirection: Axis.horizontal, itemCount: frameData.length, separatorBuilder: (_, __) => const SizedBox(width: 10), itemBuilder: (_, i) => Container(width: 128, decoration: BoxDecoration(color: RakshakColors.border, borderRadius: BorderRadius.circular(12)), child: Center(child: Text('Frame ${(frameData[i]['sequence_index'] ?? i + 1)}'))))),
      const SizedBox(height: 24), AppCard(child: Text(data?['action_items']?.toString() ?? 'No follow-up actions were returned.')), const SizedBox(height: 24), PrimaryAction(label: 'Share feedback', onPressed: diagnosisId == null ? null : () => navigateTo(context, FeedbackScreen(diagnosisId: diagnosisId))), const SizedBox(height: 10), SecondaryAction(label: 'Scan another area', onPressed: () => navigateTo(context, const NewScanScreen())), const SafetyNote()
    ]));
  }
}

class HealthyCropScreen extends StatelessWidget { const HealthyCropScreen({super.key}); @override Widget build(BuildContext context) => const ResultStateScreen(title: 'Healthy crop', icon: Icons.check_circle_outline, statusColor: RakshakColors.healthy, description: 'No significant disease signal was detected in this scan.', detail: 'Your soybean leaves look consistent across the reviewed frames.', action: 'Scan another area'); }
class UncertainResultScreen extends StatefulWidget { const UncertainResultScreen({super.key, this.diagnosisId}); final String? diagnosisId; @override State<UncertainResultScreen> createState() => _UncertainResultScreenState(); }
class _UncertainResultScreenState extends State<UncertainResultScreen> { bool requesting = false; @override Widget build(BuildContext context) => AppPage(title: 'Crop health report', onBack: () => Navigator.pop(context), child: PageContent(crossAxisAlignment: CrossAxisAlignment.center, children: [const SizedBox(height: 42), Container(width: 96, height: 96, decoration: const BoxDecoration(color: RakshakColors.warning, shape: BoxShape.circle), child: const Icon(Icons.help_outline, size: 48, color: RakshakColors.ink)), const SizedBox(height: 22), Text('Needs a closer look', textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 12), const Text('The signal is not strong enough for a reliable result.', textAlign: TextAlign.center), const SizedBox(height: 24), const AppCard(child: Text('Try a steadier video in better light, or ask an agronomist to review the evidence frames.')), const SizedBox(height: 24), PrimaryAction(label: requesting ? 'Requesting review...' : 'Request agronomist review', onPressed: requesting || widget.diagnosisId == null ? null : () async { setState(() => requesting = true); try { await ApiClient.instance.requestReview(widget.diagnosisId!); if (context.mounted) navigateTo(context, const ReviewRequestedScreen()); } catch (error) { if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Could not request review: $error'))); } finally { if (mounted) setState(() => requesting = false); } }), const SizedBox(height: 10), SecondaryAction(label: 'Scan another area', onPressed: () => navigateTo(context, const NewScanScreen())), const SafetyNote()])); }
class ResultStateScreen extends StatelessWidget { const ResultStateScreen({super.key, required this.title, required this.icon, required this.statusColor, required this.description, required this.detail, required this.action}); final String title, description, detail, action; final IconData icon; final Color statusColor; @override Widget build(BuildContext context) => AppPage(title: 'Crop health report', onBack: () => Navigator.pop(context), child: PageContent(crossAxisAlignment: CrossAxisAlignment.center, children: [const SizedBox(height: 42), Container(width: 96, height: 96, decoration: BoxDecoration(color: statusColor, shape: BoxShape.circle), child: Icon(icon, size: 48, color: RakshakColors.ink)), const SizedBox(height: 22), Text(title, textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 12), Text(description, textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodyLarge), const SizedBox(height: 24), AppCard(child: Text(detail, style: Theme.of(context).textTheme.bodyMedium)), const SizedBox(height: 24), PrimaryAction(label: action, onPressed: () => navigateTo(context, const NewScanScreen())), const SizedBox(height: 10), const SafetyNote()])); }
