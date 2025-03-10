import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";

export default function BarChart({ chartData }) {
  const chartRef = useRef(null);

  useEffect(() => {
    const ctx = chartRef.current.getContext("2d");

    // Создание графика
    const barChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: chartData.categories,
        datasets: [
          {
            label: "Риск",
            data: chartData.risk_counts,
            backgroundColor: "#e76e50",
            barPercentage: 1,
            borderRadius: 5,
          },
          {
            label: "Без риска",
            data: chartData.noRisk_counts,
            backgroundColor: "#274754",
            barPercentage: 1,
            borderRadius: 5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: "y", // Горизонтальная ориентация
        plugins: {
          legend: {
            position: "top",
          },
          title: {
            display: true,
            text: "Полное освобождение",
          },
          tooltip: {
            mode: "index",
            intersect: true,
            callbacks: {
              beforeBody: (context) => `Категория: ${context[0].label}`,
              label: (context) => {
                const datasetLabel = context.dataset.label || "";
                const value = context.raw;
                return `${datasetLabel}: ${value}`;
              },
              footer: (tooltipItems) => {
                const total = tooltipItems.reduce(
                  (sum, tooltipItem) => sum + tooltipItem.raw,
                  0
                );
                return `ИТОГО: ${total}`;
              },
            },
          },
          datalabels: {
            anchor: "center",
            align: "center",
            formatter: (value) => (value !== 0 ? value : ""),
            color: "white",
            font: {
              weight: "bold",
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            stacked: true,
          },
          y: {
            stacked: true,
          },
        },
      },
      plugins: [ChartDataLabels], // Подключаем плагин DataLabels
    });

    // Очистка при размонтировании
    return () => {
      barChart.destroy();
    };
  }, [chartData]);

  return (
    <div className="container mx-auto p-4">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <canvas ref={chartRef} className="w-full" style={{ maxWidth: "100%", height: "50vh" }}></canvas>
      </div>
    </div>
  );
};