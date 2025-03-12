import { apiClient } from './client';
import { Interaction, InteractionCreate, InteractionUpdate, InteractionEvent } from '@/lib/types';

export async function getUserInteractions(params: {
  skip?: number;
  limit?: number;
} = {}): Promise<Interaction[]> {
  const searchParams = new URLSearchParams();
  
  if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
  if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
  
  return apiClient(`/interactions?${searchParams.toString()}`);
}

export async function createInteraction(data: InteractionCreate): Promise<Interaction> {
  return apiClient('/interactions', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateInteraction(songId: number, data: InteractionUpdate): Promise<Interaction> {
  return apiClient(`/interactions/${songId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteInteraction(songId: number): Promise<void> {
  return apiClient(`/interactions/${songId}`, {
    method: 'DELETE',
  });
}

export async function trackInteractionEvent(event: InteractionEvent): Promise<{status: string}> {
  return apiClient('/interactions/events', {
    method: 'POST',
    body: JSON.stringify(event),
  });
}