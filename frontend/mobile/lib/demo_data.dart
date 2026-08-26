class DemoField {
  const DemoField({required this.name, required this.crop, required this.health, required this.status});
  final String name;
  final String crop;
  final int health;
  final String status;
}

class DemoScan {
  const DemoScan({required this.date, required this.field, required this.disease, required this.confidence, required this.severity, required this.affectedPlants});
  final String date;
  final String field;
  final String disease;
  final int confidence;
  final String severity;
  final String affectedPlants;
}

const demoFields = [
  DemoField(name: 'North plot', crop: 'Soybean', health: 72, status: 'At risk'),
  DemoField(name: 'East field', crop: 'Soybean', health: 91, status: 'Healthy'),
];

const demoScans = [
  DemoScan(date: 'Today, 09:42', field: 'North plot', disease: 'Soybean rust', confidence: 87, severity: 'Moderate', affectedPlants: '~20%'),
  DemoScan(date: '18 Aug 2026', field: 'East field', disease: 'No significant signal', confidence: 92, severity: 'Healthy', affectedPlants: '~4%'),
];

