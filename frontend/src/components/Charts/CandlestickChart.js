import React from 'react';
import Highcharts from 'highcharts/highstock';
import HighchartsReact from 'highcharts-react-official';
import HighchartsMore from 'highcharts/highcharts-more'; // Use default import

// Initialize highcharts-more
HighchartsMore(Highcharts);

const CandlestickChart = ({ chartData, containerHeight, bullTotalData, bearishTotalData, nadarayaWatsonData }) => {
  const options = {
    chart: {
      height: containerHeight,
      backgroundColor: '#181818',
    },
    title: {
      text: 'Candlestick Chart with Divergence',
      style: { color: '#fff' },
    },
    xAxis: {
      type: 'datetime',
    },
    yAxis: {
      title: {
        text: 'Price',
        style: { color: '#fff' },
      },
    },
    series: [
      {
        type: 'candlestick',
        name: 'Price',
        data: chartData,
        upColor: '#4fff56',
        color: '#ff5c5c',
        borderColor: '#fff',
        borderWidth: 1,
      },
      {
        name: 'Bullish Divergence',
        type: 'scatter',
        data: bullTotalData.map(item => [item[0], item[1] - 5]),
        marker: {
          fillColor: 'green',
          radius: 6,
        },
        tooltip: {
          pointFormat: 'Bullish Divergence: {point.x}',
        },
      },
      {
        name: 'Bearish Divergence',
        type: 'scatter',
        data: bearishTotalData.map(item => [item[0], item[1] + 5]),
        marker: {
          fillColor: 'red',
          radius: 6,
        },
        tooltip: {
          pointFormat: 'Bearish Divergence: {point.x}',
        },
      },
      {
        name: 'Nadaraya-Watson',
        data: nadarayaWatsonData.map(item => [item[0], item[1]]),
        color: '#00c0ff',
        lineWidth: 2,
        type: 'line',
      },
      {
        name: 'Upper Near - Upper Far',
        data: nadarayaWatsonData.map(item => [item[0], item[2], item[3]]),
        type: 'arearange',
        color: 'rgba(255, 0, 0, 0.4)',
        lineWidth: 0,
        enableMouseTracking: false,
        fillOpacity: 1,
      },
      {
        name: 'Upper Far - Upper Top',
        data: nadarayaWatsonData.map(item => [item[0], item[3], item[4]]),
        type: 'arearange',
        color: 'rgba(255, 0, 0, 0.2)',
        lineWidth: 0,
        enableMouseTracking: false,
        fillOpacity: 1,
      },
      {
        name: 'Lower Near - Lower Far',
        data: nadarayaWatsonData.map(item => [item[0], item[5], item[6]]),
        type: 'arearange',
        color: 'rgba(0, 255, 0, 0.4)',
        lineWidth: 0,
        enableMouseTracking: false,
        fillOpacity: 1,
      },
      {
        name: 'Lower Far - Lower Top',
        data: nadarayaWatsonData.map(item => [item[0], item[6], item[7]]),
        type: 'arearange',
        color: 'rgba(0, 255, 0, 0.2)',
        lineWidth: 0,
        enableMouseTracking: false,
        fillOpacity: 1,
      },
    ],
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default CandlestickChart;
