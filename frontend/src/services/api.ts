import { ScenarioMetadata, PipelineResults } from '../types';

const API_BASE = '/api';

export async function fetchScenarios(): Promise<ScenarioMetadata[]> {
  const res = await fetch(`${API_BASE}/scenarios`);
  if (!res.ok) throw new Error(`Failed to fetch scenarios: ${res.statusText}`);
  return res.json();
}

export async function fetchScenario(id: string): Promise<ScenarioMetadata> {
  const res = await fetch(`${API_BASE}/scenarios/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch scenario ${id}`);
  return res.json();
}

export async function processScenario(
  id: string,
  options?: { is_synthetic_stress?: boolean; start_point?: [number, number]; goal_point?: [number, number] }
): Promise<PipelineResults> {
  const res = await fetch(`${API_BASE}/scenarios/${id}/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(options || {})
  });
  if (!res.ok) throw new Error(`Pipeline processing failed: ${res.statusText}`);
  return res.json();
}

export async function triggerSensorDegradation(id: string): Promise<any> {
  const res = await fetch(`${API_BASE}/scenarios/${id}/degrade-sensor`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error(`Failed to degrade sensor`);
  return res.json();
}

export async function restoreSensor(id: string): Promise<any> {
  const res = await fetch(`${API_BASE}/scenarios/${id}/restore-sensor`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error(`Failed to restore sensor`);
  return res.json();
}

export async function fetchRos2Graph(): Promise<any> {
  const res = await fetch(`${API_BASE}/ros2/graph`);
  if (!res.ok) throw new Error(`Failed to fetch ROS 2 graph`);
  return res.json();
}
