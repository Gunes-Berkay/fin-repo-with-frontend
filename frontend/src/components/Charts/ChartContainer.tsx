import React, { useState, useEffect } from 'react';
import CandlestickChart from './CandlestickChart';
import RsiChart from './RsiChart';
import MacdChart from './MacdChart';
import VolumeChart from './VolumeChart';
import StochChart from './StochChart';
import CmfChart from './CmfChart';
import CciChart from './CciChart';
import MfiChart from './MfiChart';
import ObvChart from './ObvChart';
import AdxChart from './AdxChart';

const ChartContainer = () => {
  const [chartData, setChartData] = useState([]);
  interface IndicatorsData {
    rsi: number[][];
    macd: number[][];
    volume: number[][];
    stoch: number[][];
    cmf: number[][];
    cci: number[][];
    mfi: number[][];
    obv: number[][];
    adx: number[][];
  }

  const [indicatorsData, setIndicatorsData] = useState<IndicatorsData>({
    rsi: [],
    macd: [],
    volume: [],
    stoch: [],
    cmf: [],
    cci: [],
    mfi: [],
    obv: [],
    adx: [],
  });
  const [timeFrame, setTimeFrame] = useState('normal');
  const [containerHeight, setContainerHeight] = useState(500);
  const [containerHeightforIndicators, setContainerHeightforIndicators] = useState(300);
  const [bullTotalData, setBullTotalData] = useState([]);
  const [bearishTotalData, setBearishTotalData] = useState([]);
  const [nadarayaWatsonData, setNadarayaWatsonData] = useState([]);

  const [enabledIndicators, setEnabledIndicators] = useState({
    rsi: true,
    macd: true,
    volume: false,
    stoch: false,
    cmf: false,
    cci: false,
    mfi: false,
    obv: false,
    adx: false,
  });

  const fetchData = async (timeFrame) => {
    const response = await fetch('http://127.0.0.1:8000/charts/table/DOGEUSDTon4hlmt600/');
    const data = await response.json();

    const formattedCandlestickData = data.table_data.map(item => [
      item.datetime,
      item.open,
      item.high,
      item.low,
      item.close,
    ]);

    const formattedBullTotalData = data.table_data
    .filter(item => item.Bull_Total > 5)
    .map(item => [
      item.datetime,
      item.low,
      item.Bull_Total
    ]);

    const formattedBearishTotalData = data.table_data
    .filter(item => item.Bearish_Total > 5)
    .map(item => [
      item.datetime,
      item.high,
      item.Bearish_Total
    ]);

    const formattedNadarayaWatsonData = data.table_data.map(item => [
      item.datetime,
      item.yhat,
      item.upper_near,
      item.upper_far,
      item.upper_top,
      item.lower_near,
      item.lower_far,
      item.lower_top
    ]);


    const extractIndicatorData = (key) => data.table_data.map(item => [item.datetime, item[key]]);

    setChartData(formattedCandlestickData);
    setBullTotalData(formattedBullTotalData);
    setBearishTotalData(formattedBearishTotalData);
    setNadarayaWatsonData(formattedNadarayaWatsonData);

    setIndicatorsData({
      rsi: extractIndicatorData('rsi_14'),
      macd: extractIndicatorData('macd'),
      volume: extractIndicatorData('volume'),
      stoch: extractIndicatorData('stoch_k'),
      cmf: extractIndicatorData('cmf'),
      cci: extractIndicatorData('cci'),
      mfi: extractIndicatorData('mfi'),
      obv: extractIndicatorData('obv'),
      adx: extractIndicatorData('adx'),
    });
  };

  useEffect(() => {
    fetchData(timeFrame);
  }, [timeFrame]);

  const increaseTimeFrame = () => {
    setTimeFrame('expanded');
  };

  const decreaseTimeFrame = () => {
    setTimeFrame('normal');
  };

  const increaseHeight = () => {
    setContainerHeight(prev => prev + 100);
    setContainerHeightforIndicators(prev => prev + 50);
  };

  const decreaseHeight = () => {
    setContainerHeight(prev => prev - 100);
    setContainerHeightforIndicators(prev => prev - 50);
  };

  const handleCheckboxChange = (indicator) => {
    setEnabledIndicators(prev => ({
      ...prev,
      [indicator]: !prev[indicator],
    }));
  };

  return (
    <div>
      <button onClick={increaseTimeFrame}>🔼 Zaman Aralığını Genişlet</button>
      <button onClick={decreaseTimeFrame}>🔽 Zaman Aralığını Küçült</button>
      <button onClick={increaseHeight}>📏 Yüksekliği Artır</button>
      <button onClick={decreaseHeight}>📏 Yüksekliği Azalt</button>

      <div>
        {Object.keys(enabledIndicators).map((key) => (
          <label key={key} style={{ marginRight: '10px' }}>
            <input
              type="checkbox"
              checked={enabledIndicators[key]}
              onChange={() => handleCheckboxChange(key)}
            />
            {key.toUpperCase()}
          </label>
        ))}
      </div>
      

      <CandlestickChart chartData={chartData} containerHeight={containerHeight} bullTotalData={bullTotalData} bearishTotalData={bearishTotalData} nadarayaWatsonData={nadarayaWatsonData}/>

      {enabledIndicators.rsi && <RsiChart rsiData={indicatorsData.rsi} containerHeight={containerHeightforIndicators} />}
      {enabledIndicators.macd && <MacdChart macdData={indicatorsData.macd} containerHeight={containerHeightforIndicators} />}
      {enabledIndicators.volume && <VolumeChart volumeData={indicatorsData.volume} containerHeight={containerHeightforIndicators} />}
      {enabledIndicators.stoch && <StochChart stochData={indicatorsData.stoch} containerHeight={containerHeightforIndicators} />}
      {enabledIndicators.cmf && <CmfChart cmfData={indicatorsData.cmf} containerHeight={containerHeightforIndicators} />}
      {enabledIndicators.cci && <CciChart cciData={indicatorsData.cci} containerHeight={containerHeightforIndicators} />}
      {enabledIndicators.mfi && <MfiChart mfiData={indicatorsData.mfi} containerHeight={containerHeightforIndicators} />}
      {enabledIndicators.obv && <ObvChart obvData={indicatorsData.obv} containerHeight={containerHeightforIndicators} />}
      {enabledIndicators.adx && <AdxChart adxData={indicatorsData.adx} containerHeight={containerHeightforIndicators} />}
    </div>
  );
};

export default ChartContainer;
