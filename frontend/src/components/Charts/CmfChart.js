import React from 'react';
import Highcharts from 'highcharts/highstock';
import HighchartsReact from 'highcharts-react-official';

const CmfChart = ({ cmfData, containerHeight }) => {
  const options = {
    chart: {
      height: containerHeight,
      backgroundColor: '#181818',
    },
    xAxis: {
      type: 'datetime',
    },
    yAxis: {
      title: { text: 'CMF' },
    },
    series: [
      {
        type: 'line',
        name: 'CMF',
        data: cmfData,
        color: '#ffcc00',
      },
    ],
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default CmfChart;
