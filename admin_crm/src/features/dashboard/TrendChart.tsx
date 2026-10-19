import { useEffect, useId, useRef, useState } from 'react';
import type { TrendPoint } from './model';

const shortDate = (day: string) => `${day.slice(8, 10)}.${day.slice(5, 7)}`;
export function TrendChart({ points, bucketDays }: { points: TrendPoint[]; bucketDays: number }) {
  const gradientId = useId();
  const canvas = useRef<SVGSVGElement>(null);
  const [width, setWidth] = useState(750);
  useEffect(() => {
    const svg = canvas.current;
    if (!svg) return;
    const measure = () => setWidth(Math.max(280, Math.round(svg.getBoundingClientRect().width)));
    measure();
    if (typeof ResizeObserver === 'undefined') {
      window.addEventListener('resize', measure);
      return () => window.removeEventListener('resize', measure);
    }
    const observer = new ResizeObserver(measure);
    observer.observe(svg);
    return () => observer.disconnect();
  }, []);
  const maximum = Math.max(1, ...points.map(point => point.count));
  const tick = Math.max(1, Math.ceil(maximum / 3));
  const yMaximum = tick * 3;
  const right = width - 25;
  const x = (index: number) => points.length === 1 ? (55 + right) / 2 : 55 + index * (right - 55) / (points.length - 1);
  const y = (count: number) => 190 - count / yMaximum * 135;
  const line = points.map((point, index) => `${x(index)},${y(point.count)}`).join(' ');
  const labelEvery = Math.max(1, Math.ceil(points.length / (width < 480 ? 4 : 7)));
  const total = points.reduce((sum, point) => sum + point.count, 0);

  return (
    <div className="trend-chart">
      <svg ref={canvas} viewBox={`0 0 ${width} 240`} role="img" aria-label={`${total} ta buyurtma. ${points.map(point => `${point.day}${point.end !== point.day ? `–${point.end}` : ''}: ${point.count} ta`).join('; ')}`}>
        <defs><linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#3d75f6" stopOpacity=".18" /><stop offset="100%" stopColor="#3d75f6" stopOpacity="0" /></linearGradient></defs>
        {[0, 1, 2, 3].map(index => <g key={index}><line x1="55" x2={right} y1={190 - index * 45} y2={190 - index * 45} stroke="#e6ebf3" strokeDasharray="4 5" /><text x="26" y={195 - index * 45} fontSize="14">{index * tick}</text></g>)}
        <polygon points={`${x(0)},190 ${line} ${x(points.length - 1)},190`} fill={`url(#${gradientId})`} />
        <polyline points={line} fill="none" stroke="#3873f2" strokeWidth="3" strokeLinejoin="round" />
        {points.map((point, index) => <g key={point.day}>
          <circle cx={x(index)} cy={y(point.count)} r="4" fill="white" stroke="#3873f2" strokeWidth="2"><title>{shortDate(point.day)}{point.day !== point.end ? `–${shortDate(point.end)}` : ''}: {point.count} ta</title></circle>
          {(index % labelEvery === 0 || index === points.length - 1) && <text x={x(index)} y="224" textAnchor="middle" fontSize="14">{shortDate(point.day)}</text>}
        </g>)}
      </svg>
      <div className="chart-legend"><span className="stat-dot blue" />Yangi buyurtmalar<span className="muted">· {bucketDays === 1 ? 'kunlik' : `${bucketDays} kunlik guruhlar`}</span></div>
    </div>
  );
}
