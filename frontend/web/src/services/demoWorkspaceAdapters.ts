import type { DemoWorkspace, DemoField } from './apiClient.ts';
import type { Farm, Field } from '../types/index.ts';

export function demoWorkspaceToFarms(workspace: DemoWorkspace | null): Farm[] {
  if (!workspace || !workspace.available) return [];

  const orgName = workspace.organization?.name || 'Rakshak Demonstration Cooperative';

  if (workspace.organization?.farms && workspace.organization.farms.length > 0) {
    return workspace.organization.farms.map((farm) => {
      const mappedFields: Field[] = (farm.fields || []).map((f) => ({
        id: f.reference,
        name: f.name,
        farmId: farm.reference,
        farmName: farm.name,
        fpoName: orgName,
        district: f.district || farm.district,
        crop: f.crop || 'Soybean',
        areaAcres: f.area_hectares ? Number((f.area_hectares * 2.47105).toFixed(2)) : 0,
        healthStatus: 'Not assessed',
        latestScanDate: '',
        primaryDiseaseSignal: 'No scan recorded',
        severity: 'Uncertain',
        totalScansCount: 0,
        scanHistory: [],
      }));

      return {
        id: farm.reference,
        name: farm.name,
        fpoName: orgName,
        district: farm.district,
        ownerName: farm.owner_name,
        totalFieldsCount: mappedFields.length,
        riskStatus: 'Not assessed',
        diseaseSignalsCount: 0,
        totalScansCount: 0,
        fields: mappedFields,
        recentCases: [],
      };
    });
  }

  if (workspace.farmer?.fields && workspace.farmer.fields.length > 0) {
    const farmMap = new Map<string, DemoField[]>();
    workspace.farmer.fields.forEach((f) => {
      const list = farmMap.get(f.farm_name) || [];
      list.push(f);
      farmMap.set(f.farm_name, list);
    });

    let farmIndex = 1;
    const farms: Farm[] = [];
    farmMap.forEach((fieldItems, farmName) => {
      const farmRef = `DEMO-FARM-${String(farmIndex).padStart(2, '0')}`;
      farmIndex += 1;
      const district = fieldItems[0]?.district || 'Sehore';
      const mappedFields: Field[] = fieldItems.map((f) => ({
        id: f.reference,
        name: f.name,
        farmId: farmRef,
        farmName,
        fpoName: orgName,
        district: f.district || district,
        crop: f.crop || 'Soybean',
        areaAcres: f.area_hectares ? Number((f.area_hectares * 2.47105).toFixed(2)) : 0,
        healthStatus: 'Not assessed',
        latestScanDate: '',
        primaryDiseaseSignal: 'No scan recorded',
        severity: 'Uncertain',
        totalScansCount: 0,
        scanHistory: [],
      }));

      farms.push({
        id: farmRef,
        name: farmName,
        fpoName: orgName,
        district,
        ownerName: workspace.farmer?.display_name || 'Demo Farmer',
        totalFieldsCount: mappedFields.length,
        riskStatus: 'Not assessed',
        diseaseSignalsCount: 0,
        totalScansCount: 0,
        fields: mappedFields,
        recentCases: [],
      });
    });

    return farms;
  }

  return [];
}

export function getDemoFarmByReference(workspace: DemoWorkspace | null, ref: string): Farm | null {
  const farms = demoWorkspaceToFarms(workspace);
  return farms.find((f) => f.id === ref || f.name.toLowerCase() === ref.toLowerCase()) || null;
}

export function getDemoFieldByReference(workspace: DemoWorkspace | null, ref: string): Field | null {
  const farms = demoWorkspaceToFarms(workspace);
  for (const farm of farms) {
    const match = farm.fields.find((f) => f.id === ref || f.name.toLowerCase() === ref.toLowerCase());
    if (match) return match;
  }
  return null;
}

export function isDemoReference(id: string): boolean {
  return Boolean(id && (id.startsWith('DEMO-') || id.startsWith('demo-')));
}
