import { Farm } from '../types';

export function downloadCsv(name: string, rows: unknown[][]) {
  const cell = (value: unknown) => {
    let text = value == null ? '' : String(value);
    // Prevent user-entered field names from becoming spreadsheet formulas.
    if (/^[\s]*[=+@-]/.test(text)) text = "'" + text;
    return '"' + text.replaceAll('"', '""') + '"';
  };
  const blob = new Blob(['\uFEFF' + rows.map(row => row.map(cell).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a'); link.href = url; link.download = name; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function exportFields(farms: Farm[]) {
  downloadCsv(`rakshak-fields-${new Date().toISOString().slice(0, 10)}.csv`, [
    ['Farm', 'District', 'Field', 'Crop', 'Area (acres)', 'Latest scan', 'Indication', 'Visual severity', 'Assessment status', 'Model status'],
    ...farms.flatMap(farm => farm.fields.map(field => [farm.name, farm.district, field.name, field.crop, field.areaAcres || '', field.latestScanDate, field.primaryDiseaseSignal, field.severity, field.healthStatus, 'Baseline; field validation pending'])),
  ]);
}
