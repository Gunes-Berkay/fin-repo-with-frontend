import React from 'react';
import Highcharts from 'highcharts/highstock';
import HighchartsReact from 'highcharts-react-official';

const MacdChart = ({ macdData, containerHeight }) => {
  const options = {
    chart: {
      height: containerHeight,
      backgroundColor: '#181818',
    },
    xAxis: {
      type: 'datetime',
    },
    series: [
      {
        type: 'line',
        name: 'MACD',
        data: macdData,
        color: '#ff00ff',
      },
    ],
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default MacdChart;
