import api from './api';

export async function uploadCOE(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/api/coe/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function getCOEResults(analysisId) {
  const { data } = await api.get(`/api/coe/results/${analysisId}`);
  return data;
}

export async function getCOEHistory(skip = 0, limit = 50) {
  const { data } = await api.get('/api/coe/history', { params: { skip, limit } });
  return data;
}

export async function deleteCOEResults(analysisId) {
  await api.delete(`/api/coe/results/${analysisId}`);
}
