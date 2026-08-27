import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../widgets/app_components.dart';
import 'feedback_screens.dart';
import 'scan_screens.dart';

class CropHealthReportScreen extends StatelessWidget {
  const CropHealthReportScreen({super.key});
  @override
  Widget build(BuildContext context) => AppPage(
      title: 'Crop health report',
      onBack: () => Navigator.pop(context),
      child: PageContent(children: [
        AppCard(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Expanded(
                child: Text('Soybean rust',
                    style: Theme.of(context).textTheme.headlineSmall)),
            const StatusBadge(
                label: 'Moderate',
                color: RakshakColors.warning,
                textColor: RakshakColors.warningText)
          ]),
          const SizedBox(height: 8),
          const Text('North plot · Today, 09:42'),
          const SizedBox(height: 20),
          Text('87%', style: Theme.of(context).textTheme.displaySmall),
          const Text('Confidence across 18 usable frames')
        ])),
        const SizedBox(height: 24),
        const SectionHeading(title: 'What we saw', actionLabel: ''),
        const SizedBox(height: 8),
        const AppCard(
            child: Text(
                'A similar signal appeared across multiple leaves. This is an indication for review, not a confirmed diagnosis.')),
        const SizedBox(height: 24),
        const SectionHeading(
            title: 'Evidence frames', actionLabel: '18 frames', onAction: null),
        const SizedBox(height: 8),
        SizedBox(
            height: 104,
            child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: 4,
                separatorBuilder: (_, __) => const SizedBox(width: 10),
                itemBuilder: (_, i) => Container(
                    width: 128,
                    decoration: BoxDecoration(
                        color: i.isEven
                            ? RakshakColors.border
                            : RakshakColors.healthy,
                        borderRadius: BorderRadius.circular(12)),
                    child: Center(child: Text('Frame ${i + 1}'))))),
        const SizedBox(height: 24),
        const AppCard(
            child: Text(
                'Suggested next step\n\nWalk the north plot again in 3–5 days and consider agronomist review if the signal spreads.')),
        const SizedBox(height: 24),
        PrimaryAction(
            label: 'Share feedback',
            onPressed: () => navigateTo(context, const FeedbackScreen())),
        const SizedBox(height: 10),
        SecondaryAction(
            label: 'Scan another area',
            onPressed: () => navigateTo(context, const NewScanScreen())),
        TextButton(
            onPressed: () => navigateTo(context, const UncertainResultScreen()),
            child: const Text('View uncertain result example')),
        const SafetyNote()
      ]));
}

class HealthyCropScreen extends StatelessWidget {
  const HealthyCropScreen({super.key});
  @override
  Widget build(BuildContext context) => ResultStateScreen(
      title: 'Healthy crop',
      icon: Icons.check_circle_outline,
      statusColor: RakshakColors.healthy,
      description: 'No significant disease signal was detected in this scan.',
      detail: 'Your soybean leaves look consistent across the reviewed frames.',
      action: 'Scan another area');
}

class UncertainResultScreen extends StatelessWidget {
  const UncertainResultScreen({super.key});
  @override
  Widget build(BuildContext context) => ResultStateScreen(
      title: 'Needs a closer look',
      icon: Icons.help_outline,
      statusColor: RakshakColors.warning,
      description: 'The signal is not strong enough for a reliable result.',
      detail:
          'Try a steadier video in better light, or ask an agronomist to review the evidence frames.',
      action: 'Request review');
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
