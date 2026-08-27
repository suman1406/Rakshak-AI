import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../widgets/app_components.dart';

class FeedbackScreen extends StatefulWidget {
  const FeedbackScreen({super.key});
  @override
  State<FeedbackScreen> createState() => _FeedbackState();
}

class _FeedbackState extends State<FeedbackScreen> {
  int rating = 0;
  @override
  Widget build(BuildContext context) => AppPage(
      title: 'Share feedback',
      onBack: () => Navigator.pop(context),
      child: PageContent(children: [
        Text('Was this helpful?',
            style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 8),
        const Text('Your feedback helps improve the pilot for every field.'),
        const SizedBox(height: 24),
        AppCard(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('How close was this result?',
              style: TextStyle(fontWeight: FontWeight.w800)),
          const SizedBox(height: 12),
          Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
            for (var i = 1; i <= 5; i++)
              IconButton(
                  onPressed: () => setState(() => rating = i),
                  icon: Icon(
                      i <= rating
                          ? Icons.star_rounded
                          : Icons.star_border_rounded,
                      size: 32,
                      color: RakshakColors.warningText))
          ])
        ])),
        const SizedBox(height: 18),
        const TextField(
            maxLines: 5,
            decoration: InputDecoration(
                labelText: 'Add a note (optional)', alignLabelWithHint: true)),
        const SizedBox(height: 22),
        PrimaryAction(
            label: 'Submit feedback',
            onPressed: () => navigateTo(context, const ReviewRequestedScreen()))
      ]));
}

class ReviewRequestedScreen extends StatelessWidget {
  const ReviewRequestedScreen({super.key});
  @override
  Widget build(BuildContext context) => AppPage(
      title: 'Review requested',
      child:
          PageContent(crossAxisAlignment: CrossAxisAlignment.center, children: [
        const SizedBox(height: 80),
        Container(
            width: 92,
            height: 92,
            decoration: const BoxDecoration(
                color: RakshakColors.signal, shape: BoxShape.circle),
            child: const Icon(Icons.mark_email_read_outlined,
                size: 44, color: RakshakColors.ink)),
        const SizedBox(height: 24),
        Text('A second set of eyes is on it.',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 12),
        const Text(
            'An agronomist can review your evidence frames. We will keep this scan in your history.',
            textAlign: TextAlign.center),
        const SizedBox(height: 28),
        PrimaryAction(
            label: 'Back to my fields',
            onPressed: () =>
                Navigator.popUntil(context, (route) => route.isFirst))
      ]));
}
