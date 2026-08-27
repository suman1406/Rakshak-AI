import 'package:flutter/material.dart';
import '../core/app_theme.dart';

void navigateTo(BuildContext context, Widget page) =>
    Navigator.of(context).push(MaterialPageRoute(builder: (_) => page));

class AppPage extends StatelessWidget {
  const AppPage(
      {super.key,
      required this.title,
      required this.child,
      this.onBack,
      this.actions});
  final String title;
  final Widget child;
  final VoidCallback? onBack;
  final List<Widget>? actions;
  @override
  Widget build(BuildContext context) => Scaffold(
      appBar: AppBar(
          leading: onBack == null
              ? null
              : IconButton(
                  onPressed: onBack, icon: const Icon(Icons.arrow_back)),
          title: Text(title, style: Theme.of(context).textTheme.titleLarge),
          actions: actions),
      body: SafeArea(
          child: Center(
              child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 620),
                  child: child))));
}

class PageContent extends StatelessWidget {
  const PageContent(
      {super.key,
      required this.children,
      this.crossAxisAlignment = CrossAxisAlignment.start});
  final List<Widget> children;
  final CrossAxisAlignment crossAxisAlignment;
  @override
  Widget build(BuildContext context) => SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
      child:
          Column(crossAxisAlignment: crossAxisAlignment, children: children));
}

class PrimaryAction extends StatelessWidget {
  const PrimaryAction(
      {super.key, required this.label, required this.onPressed, this.icon});
  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  @override
  Widget build(BuildContext context) => SizedBox(
      width: double.infinity,
      child: FilledButton.icon(
          onPressed: onPressed,
          icon: icon == null ? const SizedBox.shrink() : Icon(icon),
          label: Text(label)));
}

class SecondaryAction extends StatelessWidget {
  const SecondaryAction(
      {super.key, required this.label, required this.onPressed, this.icon});
  final String label;
  final VoidCallback? onPressed;
  final IconData? icon;
  @override
  Widget build(BuildContext context) => SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
          onPressed: onPressed,
          icon: icon == null ? const SizedBox.shrink() : Icon(icon),
          label: Text(label)));
}

class AppCard extends StatelessWidget {
  const AppCard(
      {super.key,
      required this.child,
      this.padding = const EdgeInsets.all(16),
      this.color = Colors.white});
  final Widget child;
  final EdgeInsets padding;
  final Color color;
  @override
  Widget build(BuildContext context) => Container(
      width: double.infinity,
      padding: padding,
      decoration: BoxDecoration(
          color: color,
          border: Border.all(color: RakshakColors.border),
          borderRadius: BorderRadius.circular(16)),
      child: child);
}

class StatusBadge extends StatelessWidget {
  const StatusBadge(
      {super.key,
      required this.label,
      required this.color,
      required this.textColor});
  final String label;
  final Color color, textColor;
  @override
  Widget build(BuildContext context) => Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration:
          BoxDecoration(color: color, borderRadius: BorderRadius.circular(999)),
      child: Text(label,
          style: TextStyle(
              color: textColor, fontSize: 12, fontWeight: FontWeight.w800)));
}

class SectionHeading extends StatelessWidget {
  const SectionHeading(
      {super.key, required this.title, this.actionLabel = '', this.onAction});
  final String title, actionLabel;
  final VoidCallback? onAction;
  @override
  Widget build(BuildContext context) => Row(children: [
        Expanded(
            child: Text(title, style: Theme.of(context).textTheme.titleLarge)),
        if (actionLabel.isNotEmpty)
          TextButton(onPressed: onAction, child: Text(actionLabel))
      ]);
}

class SafetyNote extends StatelessWidget {
  const SafetyNote(
      {super.key,
      this.title = 'Decision support, not a confirmed diagnosis.',
      this.body =
          'Use evidence and confidence to decide whether an agronomist review is useful.'});
  final String title, body;
  @override
  Widget build(BuildContext context) => AppCard(
      color: RakshakColors.healthy,
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Icon(Icons.shield_outlined, color: RakshakColors.ink),
        const SizedBox(width: 12),
        Expanded(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 4),
          Text(body, style: Theme.of(context).textTheme.bodyMedium)
        ]))
      ]));
}

class EmptyState extends StatelessWidget {
  const EmptyState(
      {super.key,
      required this.icon,
      required this.title,
      required this.body,
      this.action});
  final IconData icon;
  final String title, body;
  final Widget? action;
  @override
  Widget build(BuildContext context) => AppCard(
          child: Column(children: [
        Icon(icon, size: 42, color: RakshakColors.leaf),
        const SizedBox(height: 12),
        Text(title,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 6),
        Text(body,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium),
        if (action != null) ...[const SizedBox(height: 16), action!]
      ]));
}
