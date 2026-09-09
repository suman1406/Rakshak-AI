import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../api_client.dart';

class EvidenceImage extends StatefulWidget {
  const EvidenceImage(
      {super.key,
      required this.path,
      required this.label,
      this.expanded = false});
  final String path, label;
  final bool expanded;
  @override
  State<EvidenceImage> createState() => _EvidenceImageState();
}

class _EvidenceImageState extends State<EvidenceImage> {
  late Future<Uint8List> image;
  @override
  void initState() {
    super.initState();
    image = ApiClient.instance.evidenceBytes(widget.path);
  }

  @override
  void didUpdateWidget(EvidenceImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.path != widget.path) {
      image = ApiClient.instance.evidenceBytes(widget.path);
    }
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<Uint8List>(
      future: image,
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          return Center(
              child: TextButton(
                  onPressed: () => setState(() =>
                      image = ApiClient.instance.evidenceBytes(widget.path)),
                  child: const Text('Retry image')));
        }
        if (!snapshot.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        final content = Image.memory(snapshot.data!,
            fit: widget.expanded ? BoxFit.contain : BoxFit.cover,
            width: double.infinity,
            semanticLabel: widget.label);
        if (widget.expanded) return InteractiveViewer(child: content);
        return InkWell(
            onTap: () => Navigator.of(context).push(MaterialPageRoute(
                builder: (_) => Scaffold(
                    appBar: AppBar(title: Text(widget.label)),
                    body: SafeArea(
                        child: EvidenceImage(
                            path: widget.path,
                            label: widget.label,
                            expanded: true))))),
            child: content);
      });
}
