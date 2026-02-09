import api from './api';

export async function analyzeSQL(sqlQuery) {
  const { data } = await api.post('/api/sql/analyze', { sql_query: sqlQuery });
  return data;
}

export async function compareSQL(sql1, sql2) {
  const { data } = await api.post('/api/sql/compare', { sql1, sql2 });
  return data;
}
