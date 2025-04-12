import React from 'react';
import Highcharts from 'highcharts/highstock';
import HighchartsReact from 'highcharts-react-official';


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
        data: bullTotalData.map(item => ({
          x:item[0],
          y:item[1]*90/100,
          bullTotal:item[2],
        })),
        marker: {
          fillColor: 'green',
          radius: 6,
        },
        tooltip: {
          pointFormatter: function() {
            return `Positive Divergence: ${this.x}<br>Price: ${this.y}<br>Positive Divergence Count: ${this.bullTotal}`;
          },
        },
      },
      {
        name: 'Bearish Divergence',
        type: 'scatter',
        data: bearishTotalData.map(item => ({
          x: item[0],
          y: item[1]*110/100,
          bearishTotal: item[2],
        })),
        marker: {
          fillColor: 'red',
          radius: 6,
        },
        tooltip: {
          pointFormatter: function() {
            return `Bearish Divergence: ${this.x}<br>Price: ${this.y}<br>Negative Divergence Count: ${this.bearishTotal}`;
          },
        }
      },
      {
        name: 'Nadaraya-Watson',
        data: nadarayaWatsonData.map(item => [item[0], item[1]]),
        color: '#00c0ff',
        lineWidth: 1,
        type: 'line',
      },
      {
        name: 'Upper Near',
        data: nadarayaWatsonData.map(item => [item[0], item[2]]),
        type: 'line',
        color: 'rgba(255, 0, 0, 0.6)',
        lineWidth: 2,
      },
      {
        name: 'Upper Far',
        data: nadarayaWatsonData.map(item => [item[0], item[3]]),
        type: 'line',
        color: 'rgba(255, 0, 0, 0.4)',
        lineWidth: 2,
      },
      {
        name: 'Upper Top',
        data: nadarayaWatsonData.map(item => [item[0],item[4]]),
        type: 'line',
        color: 'rgba(255, 0, 0, 0.2)',
        lineWidth: 2,
      },
      {
        name: 'Lower Near',
        data: nadarayaWatsonData.map(item => [item[0], item[5]]),
        type: 'line', 
        color: 'rgba(0, 255, 0, 0.6)',
        lineWidth: 2,
      },
      {
        name: 'Lower Far',
        data: nadarayaWatsonData.map(item => [item[0], item[6]]),
        type: 'line', 
        color: 'rgba(0, 255, 0, 0.4)',
        lineWidth: 2,
      },
      {
        name: 'Lower Top',
        data: nadarayaWatsonData.map(item => [item[0],item[7]]),
        type: 'line', 
        color: 'rgba(0, 255, 0, 0.2)',
        lineWidth: 2,
      },
    ],
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default CandlestickChart;
