import React from 'react';
import Highcharts from 'highcharts/highstock';
import HighchartsReact from 'highcharts-react-official';

const RsiChart = ({ rsiData, containerHeight }) => {
  const options = {
    chart: {
      height: containerHeight,
      backgroundColor: '#181818',
    },
    xAxis: {
      type: 'datetime',
    },
    yAxis: {
        plotLines: [
          {
            value: 30,
            color: '#ffcc00',
            width: 2,
            label: {
              text: '30 (Oversold)',
              align: 'center',
              style: {
                color: 'white',
              },
            },
          },
          {
            value: 70,
            color: '#ffcc00',
            width: 2,
            label: {
              text: '70 (Overbought)',
              align: 'center',
              style: {
                color: 'white',
              },
            },
          },
        ],
      },
    series: [
      {
        type: 'line',
        name: 'RSI (14)',
        data: rsiData,
        color: '#ffcc00',
      },
    ],
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default RsiChart;
