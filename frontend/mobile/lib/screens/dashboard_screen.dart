import 'package:flutter/material.dart';
import '../api_client.dart';
import '../core/app_theme.dart';
import '../widgets/app_components.dart';
import 'history_screen.dart';
import 'field_setup_screen.dart';
import 'profile_screen.dart';
import 'scan_screens.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int tab = 0;
  int revision = 0;
  @override
  Widget build(BuildContext context) => Scaffold(
        body: SafeArea(
            child: [
          DashboardTab(key: ValueKey('home-$revision')),
          DashboardTab(key: ValueKey('fields-$revision'), fieldsOnly: true),
          const SizedBox.shrink(),
          const ScanHistoryScreen(),
          const ProfileScreen()
        ][tab]),
        bottomNavigationBar: NavigationBar(
            selectedIndex: tab,
            onDestinationSelected: (value) async {
              if (value == 2) {
                await Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const NewScanScreen()));
                if (mounted) setState(() => revision++);
              } else {
                setState(() => tab = value);
              }
            },
            destinations: const [
              NavigationDestination(
                  icon: Icon(Icons.home_outlined),
                  selectedIcon: Icon(Icons.home),
                  label: 'Home'),
              NavigationDestination(
                  icon: Icon(Icons.grass_outlined),
                  selectedIcon: Icon(Icons.grass),
                  label: 'Fields'),
              NavigationDestination(
                  icon: Icon(Icons.add_circle_outline, size: 30),
                  label: 'Scan'),
              NavigationDestination(
                  icon: Icon(Icons.history), label: 'History'),
              NavigationDestination(
                  icon: Icon(Icons.person_outline), label: 'Profile'),
            ]),
      );
}

class DashboardTab extends StatefulWidget {
  const DashboardTab({super.key, this.fieldsOnly = false});
  final bool fieldsOnly;
  @override
  State<DashboardTab> createState() => _DashboardTabState();
}

class _DashboardTabState extends State<DashboardTab> {
  late Future<_DashboardData> data;
  @override
  void initState() {
    super.initState();
    data = _load();
  }

  Future<_DashboardData> _load() async {
    final values = await Future.wait([
      ApiClient.instance.currentUser(),
      ApiClient.instance.listFields(),
      ApiClient.instance.listVideos()
    ]);
    return _DashboardData(
        user: values[0] as Map<String, dynamic>,
        fields: values[1] as List<Map<String, dynamic>>,
        videos: values[2] as List<Map<String, dynamic>>);
  }

  Future<void> open(Widget page) async {
    await Navigator.of(context).push(MaterialPageRoute(builder: (_) => page));
    if (mounted) setState(() => data = _load());
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<_DashboardData>(
      future: data,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return PageContent(children: [
            Text('Your fields',
                style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 20),
            const AppCard(
                child: Text(
                    'Could not load your field records. Check your connection and try again.')),
            const SizedBox(height: 16),
            PrimaryAction(
                label: 'Try again',
                onPressed: () => setState(() => data = _load()))
          ]);
        }
        final value = snapshot.data!;
        final latest = <String, Map<String, dynamic>>{};
        for (final video in value.videos) {
          latest.putIfAbsent(video['field_id'].toString(), () => video);
        }
        final name = (value.user['display_name']?.toString() ?? 'farmer')
            .split(' ')
            .first;
        return RefreshIndicator(
            onRefresh: () async {
              final pending = _load();
              setState(() => data = pending);
              try {
                await pending;
              } catch (_) {/* FutureBuilder displays retry. */}
            },
            child: PageContent(children: [
              const SizedBox(height: 12),
              const RakshakBrand(),
              const SizedBox(height: 26),
              Text(
                  widget.fieldsOnly ? 'Your fields' : 'Your fields,\nin focus.',
                  style: Theme.of(context)
                      .textTheme
                      .displaySmall
                      ?.copyWith(letterSpacing: -1.4)),
              const SizedBox(height: 10),
              Text(
                  'Hello, $name. ${widget.fieldsOnly ? 'Keep every observation with its field.' : 'A little closer to your crop, every visit.'}'),
              const SizedBox(height: 24),
              if (!widget.fieldsOnly)
                _CapturePanel(onRecord: () => open(const NewScanScreen())),
              const SizedBox(height: 28),
              SectionHeading(
                  title: 'Your fields',
                  actionLabel: 'Add field',
                  onAction: () => open(const FieldSetupScreen())),
              const SizedBox(height: 12),
              if (value.fields.isEmpty)
                const EmptyState(
                    icon: Icons.grass_outlined,
                    title: 'Start with your first field',
                    body:
                        'Give it a name you will recognize when you return. Your scans stay with this field.'),
              for (final field
                  in (widget.fieldsOnly ? value.fields : value.fields.take(3)))
                Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: _FieldCard(
                        field: field,
                        latestVideo: latest[field['id'].toString()],
                        onTap: () => open(FieldDetailsScreen(
                            field: field,
                            latestVideo: latest[field['id'].toString()])))),
              if (!widget.fieldsOnly) ...[
                const SizedBox(height: 20),
                const SectionHeading(title: 'Recent scans'),
                const SizedBox(height: 12),
                if (value.videos.isEmpty)
                  const Text('Your first scan will appear here after upload.'),
                for (final video in value.videos.take(5))
                  Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: InkWell(
                          onTap: () => open(AnalyzingCropHealthScreen(
                              videoId: video['video_id'].toString())),
                          child: AppCard(
                              child: Row(children: [
                            const Icon(Icons.video_file_outlined),
                            const SizedBox(width: 12),
                            Expanded(
                                child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                  Text(_readable(video['status']),
                                      style: Theme.of(context)
                                          .textTheme
                                          .titleMedium),
                                  Text(_date(video['created_at']),
                                      style: const TextStyle(
                                          color: RakshakColors.leaf))
                                ])),
                            const Icon(Icons.chevron_right)
                          ])))),
                const SizedBox(height: 16),
                const SafetyNote(),
              ],
            ]));
      });
}

class _CapturePanel extends StatelessWidget {
  const _CapturePanel({required this.onRecord});
  final VoidCallback onRecord;
  @override
  Widget build(BuildContext context) => Container(
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
            color: RakshakColors.ink, borderRadius: BorderRadius.circular(24)),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Image.asset('assets/soybean-field.png',
              height: 130,
              width: double.infinity,
              fit: BoxFit.cover,
              excludeFromSemantics: true),
          Padding(
              padding: const EdgeInsets.all(22),
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Take a closer look.',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 25,
                            fontWeight: FontWeight.w700,
                            letterSpacing: -.5)),
                    const SizedBox(height: 8),
                    const Text(
                        'Record several plants. Keep the evidence. Decide what to do next.',
                        style:
                            TextStyle(color: Color(0xffe3eedd), fontSize: 15)),
                    const SizedBox(height: 20),
                    PrimaryAction(
                        label: 'Record a scan',
                        icon: Icons.videocam_outlined,
                        onPressed: onRecord),
                    const SizedBox(height: 12),
                    const Text('Soybean · 10–30 seconds',
                        style:
                            TextStyle(color: Color(0xffd4dfd7), fontSize: 13)),
                  ])),
        ]),
      );
}

String _readable(dynamic value) =>
    (value?.toString() ?? 'No scans yet').replaceAll('_', ' ');
String _date(dynamic value) {
  final date = DateTime.tryParse(value?.toString() ?? '')?.toLocal();
  return date == null
      ? 'Date unavailable'
      : '${date.day}/${date.month}/${date.year} · ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
}

class _DashboardData {
  const _DashboardData(
      {required this.user, required this.fields, required this.videos});
  final Map<String, dynamic> user;
  final List<Map<String, dynamic>> fields, videos;
}

class _FieldCard extends StatelessWidget {
  const _FieldCard(
      {required this.field, required this.latestVideo, required this.onTap});
  final Map<String, dynamic> field;
  final Map<String, dynamic>? latestVideo;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: AppCard(
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(field['name']?.toString() ?? 'Field',
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 6),
        Text(field['area_hectares'] == null
            ? 'Soybean · Area not recorded'
            : 'Soybean · ${field['area_hectares']} ha'),
        const SizedBox(height: 14),
        Wrap(
            spacing: 8,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              StatusBadge(
                  label: _readable(latestVideo?['status']),
                  color: RakshakColors.healthy,
                  textColor: RakshakColors.ink),
              const Icon(Icons.arrow_forward, size: 18)
            ]),
      ])));
}

class FieldDetailsScreen extends StatelessWidget {
  const FieldDetailsScreen({super.key, required this.field, this.latestVideo});
  final Map<String, dynamic> field;
  final Map<String, dynamic>? latestVideo;
  @override
  Widget build(BuildContext context) => AppPage(
      title: field['name']?.toString() ?? 'Field',
      onBack: () => Navigator.pop(context),
      child: PageContent(children: [
        AppCard(
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(field['name']?.toString() ?? 'Field',
              style: Theme.of(context).textTheme.headlineSmall),
          const SizedBox(height: 8),
          const Text('Soybean'),
          Text(field['area_hectares'] == null
              ? 'Area not recorded'
              : '${field['area_hectares']} hectares')
        ])),
        const SizedBox(height: 24),
        const SectionHeading(title: 'Latest scan'),
        const SizedBox(height: 12),
        Text(latestVideo == null
            ? 'No scan has been recorded yet.'
            : '${_readable(latestVideo!['status'])} · ${_date(latestVideo!['created_at'])}'),
        if (latestVideo != null) ...[
          const SizedBox(height: 16),
          SecondaryAction(
              label: 'View scan',
              onPressed: () => navigateTo(
                  context,
                  AnalyzingCropHealthScreen(
                      videoId: latestVideo!['video_id'].toString())))
        ],
        const SizedBox(height: 24),
        PrimaryAction(
            label: 'Scan this field',
            icon: Icons.videocam_outlined,
            onPressed: () => navigateTo(context,
                NewScanScreen(initialFieldId: field['id'].toString()))),
      ]));
}
