import assert from 'node:assert/strict';
import test from 'node:test';
import { demoWorkspaceToFarms, getDemoFarmByReference, getDemoFieldByReference, isDemoReference } from '../src/services/demoWorkspaceAdapters.ts';

const sampleWorkspacePayload = {
  available: true,
  message: "Demo workspace available",
  organization: {
    name: "Rakshak Demonstration Cooperative",
    farms: [
      {
        reference: "DEMO-FARM-01",
        name: "Sehore Demo Plot Alpha",
        district: "Sehore",
        owner_name: "Rakshak Demonstration Cooperative",
        fields: [
          { reference: "DEMO-FLD-01", name: "North Soybean Plot 1", farm_name: "Sehore Demo Plot Alpha", district: "Sehore", crop: "Soybean", area_hectares: 2.5, scan_count: 0 },
          { reference: "DEMO-FLD-02", name: "South Soybean Plot 2", farm_name: "Sehore Demo Plot Alpha", district: "Sehore", crop: "Soybean", area_hectares: 3.1, scan_count: 0 }
        ]
      },
      {
        reference: "DEMO-FARM-02",
        name: "Dewas Demo Plot Beta",
        district: "Dewas",
        owner_name: "Rakshak Demonstration Cooperative",
        fields: [
          { reference: "DEMO-FLD-03", name: "Dewas East Field 1", farm_name: "Dewas Demo Plot Beta", district: "Dewas", crop: "Soybean", area_hectares: 1.8, scan_count: 0 }
        ]
      }
    ],
    metrics: { total_farms: 2, total_fields: 3, videos: 0, reports: 0 }
  },
  farmer: null,
  agronomist: null,
  admin: null
};

test('demoWorkspaceToFarms converts DemoWorkspace API response to Farm[]', () => {
  const farms = demoWorkspaceToFarms(sampleWorkspacePayload);
  assert.equal(farms.length, 2);

  const farm1 = farms[0];
  assert.equal(farm1.id, 'DEMO-FARM-01');
  assert.equal(farm1.name, 'Sehore Demo Plot Alpha');
  assert.equal(farm1.fpoName, 'Rakshak Demonstration Cooperative');
  assert.equal(farm1.district, 'Sehore');
  assert.equal(farm1.riskStatus, 'Not assessed');
  assert.equal(farm1.fields.length, 2);

  const field1 = farm1.fields[0];
  assert.equal(field1.id, 'DEMO-FLD-01');
  assert.equal(field1.name, 'North Soybean Plot 1');
  assert.equal(field1.crop, 'Soybean');
  assert.equal(field1.healthStatus, 'Not assessed');
  assert.equal(field1.latestScanDate, '');
  assert.equal(field1.totalScansCount, 0);
  assert.deepEqual(field1.scanHistory, []);
});

test('getDemoFarmByReference finds farm by reference ID or name', () => {
  const farm = getDemoFarmByReference(sampleWorkspacePayload, 'DEMO-FARM-02');
  assert.ok(farm);
  assert.equal(farm.name, 'Dewas Demo Plot Beta');

  const missing = getDemoFarmByReference(sampleWorkspacePayload, 'NON-EXISTENT');
  assert.equal(missing, null);
});

test('getDemoFieldByReference finds field across all demo farms', () => {
  const field = getDemoFieldByReference(sampleWorkspacePayload, 'DEMO-FLD-03');
  assert.ok(field);
  assert.equal(field.name, 'Dewas East Field 1');
  assert.equal(field.farmId, 'DEMO-FARM-02');

  const missing = getDemoFieldByReference(sampleWorkspacePayload, 'NON-EXISTENT');
  assert.equal(missing, null);
});

test('isDemoReference identifies demo references correctly', () => {
  assert.equal(isDemoReference('DEMO-FARM-01'), true);
  assert.equal(isDemoReference('DEMO-FLD-12'), true);
  assert.equal(isDemoReference('demo-farm-01'), true);
  assert.equal(isDemoReference('c3e98124-1111-2222-3333-444455556666'), false);
  assert.equal(isDemoReference(''), false);
});
