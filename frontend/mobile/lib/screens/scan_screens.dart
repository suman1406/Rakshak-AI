import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import '../core/app_theme.dart';
import '../api_client.dart';
import '../widgets/app_components.dart';
import 'report_screens.dart';

class NewScanScreen extends StatefulWidget { const NewScanScreen({super.key}); @override State<NewScanScreen> createState() => _NewScanState(); }
class _NewScanState extends State<NewScanScreen> {
  final formKey = GlobalKey<FormState>(); String? fileName; String? filePath; String? uploadedVideoId; String? uploadError; String fieldId = 'field-north-plot'; List<Map<String, dynamic>> availableFields = []; bool consent = false; bool uploading = false;
  @override void initState() { super.initState(); _loadFields(); }
  Future<void> _loadFields() async { try { final fields = await ApiClient.instance.listFields(); if (!mounted || fields.isEmpty) return; setState(() { availableFields = fields; fieldId = fields.first['id'].toString(); }); } catch (_) {} }
  Future<void> chooseVideo() async { final result = await FilePicker.platform.pickFiles(type: FileType.video, withData: false); if (result != null) setState(() { fileName = result.files.single.name; filePath = result.files.single.path; }); }
  Future<void> recordVideo() async { final capturedPath = await Navigator.of(context).push<String>(MaterialPageRoute(builder: (_) => const CameraGuidanceScreen())); if (!mounted || capturedPath == null) return; setState(() { filePath = capturedPath; fileName = capturedPath.split(RegExp(r'[/\\]')).last; }); }
  Future<void> continueToQualityCheck() async {
    if (!formKey.currentState!.validate() || uploading || fileName == null || !consent) return;
    setState(() => uploading = true);
    if (filePath != null) {
      try { final upload = await ApiClient.instance.uploadVideo(fieldId: fieldId, filePath: filePath!, consent: consent); uploadedVideoId = upload['video_id'] as String?; }
      catch (exception) { if (mounted) setState(() { uploadError = exception.toString(); uploading = false; }); return; }
    }
    if (!mounted) return;
    setState(() => uploading = false);
    navigateTo(context, VideoQualityCheckScreen(videoId: uploadedVideoId));
  }
  @override
  Widget build(BuildContext context) => AppPage(title: 'New scan', onBack: () => Navigator.pop(context), child: PageContent(children: [Text('Capture a clear view', style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 8), const Text('Choose the crop and field, then send a short walkthrough video.'), const SizedBox(height: 24), Form(key: formKey, child: Column(children: [TextFormField(initialValue: 'Soybean', decoration: const InputDecoration(labelText: 'Crop', prefixIcon: Icon(Icons.grass_outlined)), validator: requiredScanField), const SizedBox(height: 14), DropdownButtonFormField<String>(value: fieldId, decoration: const InputDecoration(labelText: 'Field', prefixIcon: Icon(Icons.location_on_outlined)), items: (availableFields.isEmpty ? [{'id': 'field-north-plot', 'name': 'North plot'}] : availableFields).map((field) => DropdownMenuItem(value: field['id'].toString(), child: Text(field['name']?.toString() ?? 'Field'))).toList(), onChanged: (value) => setState(() => fieldId = value ?? fieldId), validator: (value) => value == null || value.isEmpty ? 'Select a field' : null)])), const SizedBox(height: 20), AppCard(child: Column(children: [Icon(fileName == null ? Icons.video_file_outlined : Icons.check_circle_rounded, color: fileName == null ? RakshakColors.leaf : RakshakColors.ink, size: 44), const SizedBox(height: 8), Text(fileName ?? 'No video selected', style: Theme.of(context).textTheme.titleMedium), const SizedBox(height: 4), const Text('MP4 or MOV · up to 100 MB'), const SizedBox(height: 14), SecondaryAction(label: 'Choose video', icon: Icons.upload_file_rounded, onPressed: chooseVideo), const SizedBox(height: 10), SecondaryAction(label: 'Record in app', icon: Icons.videocam_outlined, onPressed: recordVideo)])), if (uploadError != null) ...[const SizedBox(height: 12), AppCard(color: RakshakColors.error, child: Text('Upload failed: $uploadError', style: const TextStyle(color: RakshakColors.errorText)))], const SizedBox(height: 12), CheckboxListTile(contentPadding: EdgeInsets.zero, value: consent, onChanged: (value) => setState(() { consent = value ?? false; uploadError = null; }), controlAffinity: ListTileControlAffinity.leading, title: const Text('I understand this is decision support, not a confirmed diagnosis.')), const SizedBox(height: 8), PrimaryAction(label: uploading ? 'Uploading...' : 'Continue to quality check', icon: Icons.arrow_forward_rounded, onPressed: fileName != null && consent && !uploading ? continueToQualityCheck : null), const SizedBox(height: 16), const SafetyNote()]));
}
String? requiredScanField(String? value) => value == null || value.trim().isEmpty ? 'Required' : null;

class CameraGuidanceScreen extends StatefulWidget {
  const CameraGuidanceScreen({super.key});
  @override State<CameraGuidanceScreen> createState() => _CameraGuidanceState();
}

class _CameraGuidanceState extends State<CameraGuidanceScreen> {
  bool capturing = false;

  Future<void> captureVideo() async {
    setState(() => capturing = true);
    final cameraStatus = await Permission.camera.request();
    final microphoneStatus = await Permission.microphone.request();
    if (!mounted) return;
    if (!cameraStatus.isGranted || !microphoneStatus.isGranted) {
      setState(() => capturing = false);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Camera and microphone access are required to record a field video.')));
      return;
    }
    final video = await ImagePicker().pickVideo(source: ImageSource.camera, maxDuration: const Duration(seconds: 15));
    if (!mounted) return;
    setState(() => capturing = false);
    if (video != null) Navigator.of(context).pop(video.path);
  }

  @override
  Widget build(BuildContext context) {
    return AppPage(
      title: 'Camera guidance',
      onBack: () => Navigator.pop(context),
      child: Column(children: [
        Expanded(
          child: Container(
            color: RakshakColors.ink,
            alignment: Alignment.center,
            child: Container(
              width: 220,
              height: 300,
              decoration: BoxDecoration(border: Border.all(color: RakshakColors.signal, width: 2), borderRadius: BorderRadius.circular(22)),
              child: const Center(child: Icon(Icons.eco_rounded, color: RakshakColors.signal, size: 76)),
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(20),
          child: Column(children: [
            const Text('Move slowly and keep leaves inside the frame.', textAlign: TextAlign.center),
            const SizedBox(height: 14),
            PrimaryAction(label: capturing ? 'Opening camera...' : 'Capture video', icon: Icons.fiber_manual_record, onPressed: capturing ? null : captureVideo),
          ]),
        ),
      ]),
    );
  }
}

class VideoQualityCheckScreen extends StatelessWidget {
  const VideoQualityCheckScreen({super.key, this.videoId, this.filePath});
  final String? videoId;
  final String? filePath;
  @override
  Widget build(BuildContext context) => AppPage(title: 'Video quality check', onBack: () => Navigator.pop(context), child: PageContent(children: [AppCard(child: Column(children: [Container(height: 160, decoration: BoxDecoration(color: RakshakColors.border, borderRadius: BorderRadius.circular(12)), child: const Center(child: Icon(Icons.play_circle_outline, color: RakshakColors.ink, size: 58))), const SizedBox(height: 12), Row(children: [const Icon(Icons.check_circle_rounded, color: RakshakColors.ink), const SizedBox(width: 8), Expanded(child: Text(filePath == null ? 'Video is ready to analyze' : 'Video captured and ready to analyze', style: const TextStyle(fontWeight: FontWeight.w800)))])])), const SizedBox(height: 24), const SectionHeading(title: 'Quality signals'), const SizedBox(height: 8), for (final signal in ['Good lighting', 'Steady movement', 'Crop visible across frames']) Padding(padding: const EdgeInsets.only(bottom: 10), child: AppCard(child: Row(children: [const Icon(Icons.check_circle_outline, color: RakshakColors.ink), const SizedBox(width: 12), Text(signal)]))), const SizedBox(height: 10), PrimaryAction(label: 'Start analysis', icon: Icons.auto_awesome, onPressed: () => navigateTo(context, AnalyzingCropHealthScreen(videoId: videoId))), TextButton(onPressed: () => navigateTo(context, const QualityCheckFailedScreen()), child: const Text('Try another video'))]));
}

class QualityCheckFailedScreen extends StatelessWidget {
  const QualityCheckFailedScreen({super.key});
  @override
  Widget build(BuildContext context) => AppPage(title: 'Video needs another try', onBack: () => Navigator.pop(context), child: PageContent(crossAxisAlignment: CrossAxisAlignment.center, children: [const SizedBox(height: 64), const Icon(Icons.videocam_off_outlined, color: RakshakColors.warningText, size: 72), const SizedBox(height: 20), Text('We could not use this video', textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 10), const Text('Try better light, slower movement, and keep the crop visible in every frame.', textAlign: TextAlign.center), const SizedBox(height: 24), PrimaryAction(label: 'Try again', onPressed: () => navigateTo(context, const NewScanScreen()))]));
}

class AnalyzingCropHealthScreen extends StatefulWidget { const AnalyzingCropHealthScreen({super.key, this.videoId}); final String? videoId; @override State<AnalyzingCropHealthScreen> createState() => _AnalyzingState(); }
class _AnalyzingState extends State<AnalyzingCropHealthScreen> {
  int current = 0;
  @override void initState() { super.initState(); Future.delayed(const Duration(milliseconds: 800), () { if (mounted) setState(() => current = 1); }); Future.delayed(const Duration(milliseconds: 1600), () { if (mounted) setState(() => current = 2); }); if (widget.videoId != null) _pollBackend(); }
  Future<void> _pollBackend() async { for (var attempt = 0; attempt < 6; attempt++) { try { final status = await ApiClient.instance.videoStatus(widget.videoId!); if (!mounted) return; if (status['status'] == 'ready' || status['status'] == 'insufficient_evidence') { setState(() => current = 3); return; } } catch (_) { return; } await Future.delayed(const Duration(seconds: 1)); } }
  @override Widget build(BuildContext context) => AppPage(title: 'Analyzing crop health', child: PageContent(crossAxisAlignment: CrossAxisAlignment.center, children: [const SizedBox(height: 44), const Icon(Icons.auto_awesome, color: RakshakColors.ink, size: 56), const SizedBox(height: 18), Text('Reading your field', style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 8), const Text('Comparing multiple moments for a clearer signal.', textAlign: TextAlign.center), const SizedBox(height: 28), for (var i = 0; i < 4; i++) ListTile(leading: Icon(i <= current ? Icons.check_circle_rounded : Icons.radio_button_unchecked, color: i <= current ? RakshakColors.ink : RakshakColors.border), title: Text(['Extracting frames', 'Checking crop visibility', 'Comparing health signals', 'Preparing your report'][i])), const SizedBox(height: 18), PrimaryAction(label: 'View report', onPressed: current >= 3 || widget.videoId == null ? () => navigateTo(context, CropHealthReportScreen(videoId: widget.videoId)) : null)]));
}
