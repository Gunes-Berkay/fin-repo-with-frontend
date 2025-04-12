import React from 'react';
import Highcharts from 'highcharts/highstock';
import HighchartsReact from 'highcharts-react-official';

const CciChart = ({ cciData, containerHeight }) => {
  const options = {
    chart: {
      height: containerHeight,
      backgroundColor: '#181818',
    },
    xAxis: {
      type: 'datetime',
    },
    yAxis: {
      title: { text: 'CCI' },
    },
    series: [
      {
        type: 'line',
        name: 'CCI',
        data: cciData,
        color: '#ffcc00',
      },
    ],
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default CciChart;
