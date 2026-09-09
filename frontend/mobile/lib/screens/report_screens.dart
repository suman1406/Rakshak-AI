import 'package:flutter/material.dart';
import '../api_client.dart';
import '../core/app_theme.dart';
import '../widgets/app_components.dart';
import '../widgets/evidence_image.dart';
import 'feedback_screens.dart';
import 'scan_screens.dart';

class CropHealthReportScreen extends StatefulWidget {
  const CropHealthReportScreen({super.key, this.videoId});
  final String? videoId;
  @override
  State<CropHealthReportScreen> createState() => _ReportState();
}

class _ReportState extends State<CropHealthReportScreen> {
  bool retrying = false;
  Future<void> retryScan() async {
    setState(() => retrying = true);
    try {
      await ApiClient.instance.retryVideo(widget.videoId!);
      if (mounted) {
        Navigator.of(context).pushReplacement(MaterialPageRoute(
            builder: (_) =>
                AnalyzingCropHealthScreen(videoId: widget.videoId!)));
      }
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text(safeErrorMessage(error,
                fallback: 'Could not retry. Please try again.'))));
      }
    } finally {
      if (mounted) setState(() => retrying = false);
    }
  }

  Future<Map<String, dynamic>>? analysis;
  Future<List<Map<String, dynamic>>>? frames;
  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    if (widget.videoId != null) {
      analysis = ApiClient.instance.videoAnalysis(widget.videoId!);
      frames = ApiClient.instance.evidenceFrames(widget.videoId!);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (analysis == null) {
      return AppPage(
          title: 'Crop health report',
          onBack: () => Navigator.pop(context),
          child: const PageContent(children: [
            AppCard(
                child: Text(
                    'A video identifier is required to load a real report.'))
          ]));
    }
    return FutureBuilder<Map<String, dynamic>>(
        future: analysis,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Scaffold(
                body: Center(child: CircularProgressIndicator()));
          }
          if (snapshot.hasError) {
            return AppPage(
                title: 'Crop health report',
                onBack: () => Navigator.pop(context),
                child: PageContent(children: [
                  const AppCard(
                      child: Text('This report is temporarily unavailable.')),
                  PrimaryAction(
                      label: 'Try again', onPressed: () => setState(_load))
                ]));
          }
          return FutureBuilder<List<Map<String, dynamic>>>(
              future: frames,
              builder: (context, frameSnapshot) => _report(
                  context,
                  snapshot.data,
                  frameSnapshot.data ?? const [],
                  frameSnapshot.hasError,
                  frameSnapshot.connectionState != ConnectionState.done));
        });
  }

  Widget _report(
      BuildContext context,
      Map<String, dynamic>? data,
      List<Map<String, dynamic>> frameData,
      bool frameError,
      bool framesLoading) {
    final diagnosis =
        (data?['diagnosis'] as Map?)?.cast<String, dynamic>() ?? {};
    final evidence = (data?['evidence'] as Map?)?.cast<String, dynamic>() ?? {};
    final disease = diagnosis['disease']?.toString() ?? 'Soybean health signal';
    final confidence =
        ((diagnosis['confidence'] as num?)?.toDouble() ?? 0) * 100;
    final diagnosisId = data?['diagnosis_id']?.toString();
    final state = data?['result_state']?.toString();
    if (state == 'failed') {
      return AppPage(
          title: 'Scan interrupted',
          onBack: () => Navigator.pop(context),
          child: PageContent(children: [
            const AppCard(
                child: Text(
                    'Your saved video could not be processed. You can retry without uploading again.')),
            const SizedBox(height: 20),
            PrimaryAction(
                label: retrying ? 'Requesting retry…' : 'Retry saved scan',
                onPressed: retrying ? null : retryScan),
            const SizedBox(height: 12),
            SecondaryAction(
                label: 'Record another video',
                onPressed: () => navigateTo(context, const NewScanScreen()))
          ]));
    }
    if (state == 'insufficient_evidence') {
      return ResultStateScreen(
          title: state == 'failed'
              ? 'Scan could not complete'
              : 'Video needs another try',
          icon: Icons.videocam_off_outlined,
          statusColor: RakshakColors.warning,
          description: data?['retake_guidance']?.toString() ??
              'Please capture another video.',
          detail: 'No diagnosis was created for this scan.',
          action: 'Scan another area');
    }
    final uncertain = state == 'unknown' || state == 'unknown_other';
    final review = (data?['expert_review'] as Map?)?.cast<String, dynamic>();
    return AppPage(
        title: 'Crop health report',
        onBack: () => Navigator.pop(context),
        child: PageContent(children: [
          AppCard(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                Row(children: [
                  Expanded(
                      child: Text(
                          uncertain
                              ? 'Needs a closer look'
                              : disease.replaceAll('_', ' '),
                          style: Theme.of(context).textTheme.headlineSmall)),
                  const StatusBadge(
                      label: 'AI indication',
                      color: RakshakColors.warning,
                      textColor: RakshakColors.warningText)
                ]),
                const SizedBox(height: 8),
                const Text(
                    'Decision support only — not a confirmed diagnosis.'),
                const SizedBox(height: 20),
                Text('${confidence.round()}%',
                    style: Theme.of(context).textTheme.displaySmall),
                Text(
                    'Model confidence · ${evidence['supporting_frames'] ?? 0} supporting frames')
              ])),
          const SizedBox(height: 16),
          const Text(
              'Pilot baseline: crop identity, confidence and visual severity are not field-validated.'),
          if (review != null)
            Padding(
                padding: const EdgeInsets.only(top: 20),
                child: AppCard(
                    child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                      const Text('Agronomist review',
                          style: TextStyle(
                              fontSize: 18, fontWeight: FontWeight.w700)),
                      const SizedBox(height: 8),
                      Text(review['status'] == 'completed'
                          ? review['disease'].toString()
                          : 'Review request saved'),
                      if (review['notes'] != null)
                        Text(review['notes'].toString())
                    ]))),
          const SizedBox(height: 24),
          const SectionHeading(title: 'What we saw'),
          const SizedBox(height: 8),
          AppCard(
              child: Text(data?['explanation']?.toString() ??
                  'No explanation was returned for this analysis.')),
          const SizedBox(height: 24),
          SectionHeading(
              title: 'Evidence frames',
              actionLabel: '${frameData.length} frames'),
          const SizedBox(height: 8),
          SizedBox(
              height: 104,
              child: framesLoading
                  ? const Center(child: CircularProgressIndicator())
                  : frameError
                      ? AppCard(
                          child: TextButton(
                              onPressed: () => setState(() => frames = ApiClient
                                  .instance
                                  .evidenceFrames(widget.videoId!)),
                              child: const Text(
                                  'Could not load evidence. Try again.')))
                      : frameData.isEmpty
                          ? const AppCard(
                              child: Text(
                                  'No evidence frames are available for this scan.'))
                          : ListView.separated(
                              scrollDirection: Axis.horizontal,
                              itemCount: frameData.length,
                              separatorBuilder: (_, __) =>
                                  const SizedBox(width: 10),
                              itemBuilder: (_, i) => Container(
                                  width: 128,
                                  decoration: BoxDecoration(
                                      color: RakshakColors.border,
                                      borderRadius: BorderRadius.circular(12)),
                                  child: EvidenceImage(
                                      path:
                                          frameData[i]['evidence_url'].toString(),
                                      label: 'Observation ${frameData[i]['sequence_index']}')))),
          const SizedBox(height: 24),
          AppCard(
              child: Text(data?['action_items']?.toString() ??
                  'No follow-up actions were returned.')),
          const SizedBox(height: 24),
          if (diagnosisId != null && review == null)
            SecondaryAction(
                label: 'Request agronomist review',
                onPressed: () async {
                  try {
                    await ApiClient.instance.requestReview(diagnosisId);
                    if (mounted) setState(_load);
                  } catch (_) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                          content: Text(
                              'Could not request review. Please try again.')));
                    }
                  }
                }),
          const SizedBox(height: 12),
          PrimaryAction(
              label: 'Share feedback',
              onPressed: diagnosisId == null
                  ? null
                  : () => navigateTo(
                      context, FeedbackScreen(diagnosisId: diagnosisId))),
          const SizedBox(height: 10),
          SecondaryAction(
              label: 'Scan another area',
              onPressed: () => navigateTo(context, const NewScanScreen())),
          const SafetyNote()
        ]));
  }
}

class ResultStateScreen extends StatelessWidget {
  const ResultStateScreen(
      {super.key,
      required this.title,
      required this.icon,
      required this.statusColor,
      required this.description,
      required this.detail,
      required this.action});
  final String title, description, detail, action;
  final IconData icon;
  final Color statusColor;
  @override
  Widget build(BuildContext context) => AppPage(
      title: 'Crop health report',
      onBack: () => Navigator.pop(context),
      child:
          PageContent(crossAxisAlignment: CrossAxisAlignment.center, children: [
        const SizedBox(height: 42),
        Container(
            width: 96,
            height: 96,
            decoration:
                BoxDecoration(color: statusColor, shape: BoxShape.circle),
            child: Icon(icon, size: 48, color: RakshakColors.ink)),
        const SizedBox(height: 22),
        Text(title,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 12),
        Text(description,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyLarge),
        const SizedBox(height: 24),
        AppCard(
            child: Text(detail, style: Theme.of(context).textTheme.bodyMedium)),
        const SizedBox(height: 24),
        PrimaryAction(
            label: action,
            onPressed: () => navigateTo(context, const NewScanScreen())),
        const SizedBox(height: 10),
        const SafetyNote()
      ]));
}
