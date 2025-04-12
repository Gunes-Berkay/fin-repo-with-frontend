import React from 'react';
import Highcharts from 'highcharts/highstock';
import HighchartsReact from 'highcharts-react-official';

const VolumeChart = ({ volumeData, containerHeight }) => {
  const options = {
    chart: {
      height: containerHeight,
      backgroundColor: '#181818',
    },
    xAxis: {
      type: 'datetime',
    },
    yAxis: {
      title: { text: 'Volume' },
    },
    series: [
      {
        type: 'column',
        name: 'Volume',
        data: volumeData,
        color: '#ffcc00',
      },
    ],
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default VolumeChart;
