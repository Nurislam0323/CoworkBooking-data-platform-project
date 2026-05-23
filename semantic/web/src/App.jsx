import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import cubejs from '@cubejs-client/core';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { ChevronLeft } from 'lucide-react';
import './styles.css';

const API_URL = import.meta.env.VITE_CUBE_API_URL || 'http://localhost:4000/cubejs-api/v1';
const TOKEN = import.meta.env.VITE_CUBE_TOKEN || 'dev_secret';
const cubeApi = cubejs(TOKEN, { apiUrl: API_URL });

function fallbackRows(segment) {
  if (segment) {
    return [
      { label: 'SP-01', value: 4200, clients: 18 },
      { label: 'SP-02', value: 3100, clients: 14 },
    ];
  }
  return [
    { label: 'freelancer', value: 1350, clients: 44 },
    { label: 'startup', value: 2400, clients: 31 },
    { label: 'student', value: 700, clients: 25 },
    { label: 'corporate', value: 7200, clients: 12 },
  ];
}

function App() {
  const [segment, setSegment] = useState(null);
  const [rows, setRows] = useState(fallbackRows(null));
  const query = useMemo(() => ({
    measures: ['BookingOperations.TotalRevenue', 'BookingOperations.ClientCount'],
    dimensions: segment ? ['BookingOperations.spaceId'] : ['BookingOperations.segment'],
    filters: segment ? [{ member: 'BookingOperations.segment', operator: 'equals', values: [segment] }] : [],
  }), [segment]);

  useEffect(() => {
    cubeApi.load(query)
      .then(result => {
        const dimension = segment ? 'BookingOperations.spaceId' : 'BookingOperations.segment';
        setRows(result.tablePivot().map(r => ({
          label: r[dimension],
          value: Number(r['BookingOperations.TotalRevenue'] || 0),
          clients: Number(r['BookingOperations.ClientCount'] || 0),
        })));
      })
      .catch(() => setRows(fallbackRows(segment)));
  }, [query, segment]);

  return (
    <main>
      <header>
        <div>
          <p>CoworkBooking Data Platform</p>
          <h1>{segment ? `Drill-down: ${segment}` : 'Booking Operations'}</h1>
        </div>
        {segment && <button onClick={() => setSegment(null)}><ChevronLeft size={18}/> Segments</button>}
      </header>
      <section className="toolbar">
        <strong>{segment ? 'Площадки сегмента' : 'Клиентские сегменты'}</strong>
        <span>Выручка, клиенты, переход по клику</span>
      </section>
      <ResponsiveContainer width="100%" height={420}>
        <BarChart data={rows}>
          <XAxis dataKey="label" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" name="Revenue" fill="#2563eb" onClick={(row) => !segment && setSegment(row.label)} cursor="pointer" />
          <Bar dataKey="clients" name="Clients" fill="#10b981" />
        </BarChart>
      </ResponsiveContainer>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
