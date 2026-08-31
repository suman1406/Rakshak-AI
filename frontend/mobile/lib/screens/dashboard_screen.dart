import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../demo_data.dart';
import '../widgets/app_components.dart';
import 'history_screen.dart';
import 'profile_screen.dart';
import 'report_screens.dart';
import 'scan_screens.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int tab = 0;
  @override
  Widget build(BuildContext context) {
    final pages = [
      DashboardTab(
          onScan: () => navigateTo(context, const NewScanScreen()),
          onField: () => navigateTo(context, const FieldDetailsScreen())),
      const ScanHistoryScreen(),
      const ProfileScreen(),
    ];
    return Scaffold(
        body: SafeArea(child: pages[tab]),
        bottomNavigationBar: NavigationBar(
            selectedIndex: tab,
            onDestinationSelected: (value) => setState(() => tab = value),
            destinations: const [
              NavigationDestination(
                  icon: Icon(Icons.home_outlined),
                  selectedIcon: Icon(Icons.home_rounded),
                  label: 'Fields'),
              NavigationDestination(
                  icon: Icon(Icons.history_rounded), label: 'History'),
              NavigationDestination(
                  icon: Icon(Icons.person_outline_rounded), label: 'Profile')
            ]));
  }
}

class DashboardTab extends StatelessWidget {
  const DashboardTab({super.key, required this.onScan, required this.onField});
  final VoidCallback onScan;
  final VoidCallback onField;
  @override
  Widget build(BuildContext context) => PageContent(children: [
        const SizedBox(height: 8),
        Row(children: [
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('Tuesday, 28 August', style: Theme.of(context).textTheme.labelMedium),
            const SizedBox(height: 3),
            Text('Good morning, Arjun', style: Theme.of(context).textTheme.headlineSmall)
          ])),
          Container(width: 44, height: 44, decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)), child: IconButton(onPressed: () {}, icon: const Icon(Icons.notifications_none_rounded)))
        ]),
        const SizedBox(height: 22),
        AppCard(color: RakshakColors.ink, padding: const EdgeInsets.all(20), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [Container(width: 42, height: 42, decoration: BoxDecoration(color: RakshakColors.signal, borderRadius: BorderRadius.circular(15)), child: const Icon(Icons.eco_rounded, color: RakshakColors.ink)), const Spacer(), const StatusBadge(label: 'LIVE', color: Color(0x26d8f36a), textColor: RakshakColors.signal)]),
          const SizedBox(height: 22),
          const Text('Your fields are telling a clearer story.', style: TextStyle(color: Colors.white, fontSize: 21, height: 1.15, fontWeight: FontWeight.w800)),
          const SizedBox(height: 7),
          const Text('2 field updates are ready to review today.', style: TextStyle(color: Color(0xffc8d5cc))),
        ])),
        const SizedBox(height: 28),
        const SectionHeading(title: 'Your fields'),
        const SizedBox(height: 8),
        for (final field in demoFields)
          Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: FieldHealthCard(field: field, onTap: onField)),
        PrimaryAction(
            label: 'Start a new scan',
            icon: Icons.add_a_photo_outlined,
            onPressed: onScan),
        const SizedBox(height: 26),
        const SectionHeading(title: 'Recent scans'),
        for (final scan in demoScans)
          ScanListTile(
              scan: scan,
              onTap: () => navigateTo(context, const CropHealthReportScreen())),
        const SizedBox(height: 18),
        const SafetyNote(),
      ]);
}

class FieldHealthCard extends StatelessWidget {
  const FieldHealthCard({super.key, required this.field, required this.onTap});
  final DemoField field;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: AppCard(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Expanded(
              child: Text(field.name,
                  style: Theme.of(context).textTheme.titleMedium)),
          StatusBadge(
              label: field.status,
              color: field.status == 'Healthy'
                  ? RakshakColors.healthy
                  : RakshakColors.warning,
              textColor: field.status == 'Healthy'
                  ? RakshakColors.ink
                  : RakshakColors.warningText)
        ]),
        Text(field.crop),
        const SizedBox(height: 16),
        Row(children: [
          Expanded(
              child: ClipRRect(
                  borderRadius: BorderRadius.circular(99),
                  child: LinearProgressIndicator(
                      value: field.health / 100,
                      minHeight: 9,
                      color: field.health > 80
                          ? RakshakColors.leaf
                          : RakshakColors.warningText,
                      backgroundColor: RakshakColors.border))),
          const SizedBox(width: 12),
          Text('${field.health}% health')
        ])
      ])));
}

class ScanListTile extends StatelessWidget {
  const ScanListTile({super.key, required this.scan, required this.onTap});
  final DemoScan scan;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => Padding(
      padding: const EdgeInsets.only(top: 10),
      child: InkWell(
          onTap: onTap,
          child: AppCard(
              child: Row(children: [
            const Icon(Icons.analytics_outlined, color: RakshakColors.leaf),
            const SizedBox(width: 12),
            Expanded(
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                  Text(scan.disease,
                      style: Theme.of(context).textTheme.titleMedium),
                  Text('${scan.field} · ${scan.date}')
                ]))
          ]))));
}

class FieldDetailsScreen extends StatelessWidget {
  const FieldDetailsScreen({super.key});
  @override
  Widget build(BuildContext context) => AppPage(
      title: 'North plot',
      onBack: () => Navigator.pop(context),
      child: PageContent(children: [
        AppCard(
            child: Row(children: [
          Container(
              width: 50,
              height: 50,
              decoration: BoxDecoration(
                  color: RakshakColors.healthy,
                  borderRadius: BorderRadius.circular(14)),
              child: const Icon(Icons.crop_square_rounded)),
          const SizedBox(width: 12),
          const Expanded(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                Text('North plot',
                    style:
                        TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
                Text('Soybean · 4.2 acres')
              ]))
        ])),
        const SizedBox(height: 24),
        const SectionHeading(title: 'Health summary'),
        const SizedBox(height: 10),
        AppCard(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('72%', style: Theme.of(context).textTheme.displaySmall),
          const Text('Current health score'),
          const SizedBox(height: 16),
          const LinearProgressIndicator(
              value: .72,
              color: RakshakColors.warningText,
              backgroundColor: RakshakColors.border)
        ])),
        const SizedBox(height: 24),
        const SectionHeading(title: 'Latest evidence'),
        const SizedBox(height: 10),
        const AppCard(
            child: Text(
                'Possible soybean rust signal detected across multiple frames.\n\n87% confidence · Moderate severity')),
        const SizedBox(height: 24),
        PrimaryAction(
            label: 'Scan this field',
            icon: Icons.videocam_outlined,
            onPressed: () => navigateTo(context, const NewScanScreen()))
      ]));
}
