import React from 'react';
import Highcharts from 'highcharts/highstock';
import HighchartsReact from 'highcharts-react-official';

const StochChart = ({ stochData, containerHeight }) => {
  const options = {
    chart: {
      height: containerHeight,
      backgroundColor: '#181818',
    },
    xAxis: {
      type: 'datetime',
    },
    yAxis: {
      title: { text: 'Stochastic' },
    },
    series: [
      {
        type: 'line',
        name: 'Stochastic',
        data: stochData,
        color: '#ffcc00',
      },
    ],
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default StochChart;
