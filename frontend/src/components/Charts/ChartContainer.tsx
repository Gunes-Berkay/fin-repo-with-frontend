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

const ChartContainer = ({ interval, symbol }) => {
  const [chartData, setChartData] = useState([]);

  const [indicatorsData, setIndicatorsData] = useState({
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

  const [timeFrame, setTimeFrame] = useState(500);
  const [containerHeight, setContainerHeight] = useState(500);
  const [containerHeightforIndicators, setContainerHeightforIndicators] = useState(300);
  const [bullTotalData, setBullTotalData] = useState([]);
  const [bearishTotalData, setBearishTotalData] = useState([]);
  const [nadarayaWatsonData, setNadarayaWatsonData] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

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

  const allIndicators = [
    { key: 'rsi', label: 'RSI' },
    { key: 'macd', label: 'MACD' },
    { key: 'volume', label: 'Volume' },
    { key: 'stoch', label: 'Stochastic' },
    { key: 'cmf', label: 'CMF' },
    { key: 'cci', label: 'CCI' },
    { key: 'mfi', label: 'MFI' },
    { key: 'obv', label: 'OBV' },
    { key: 'adx', label: 'ADX' },
  ];

  const fetchData = async (timeFrame) => {
    const response = await fetch(`http://127.0.0.1:8000/charts/table/${symbol}on${interval}lmt${timeFrame}/`);
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

  const handleCheckboxChange = (indicatorKey) => {
    setEnabledIndicators(prev => ({
      ...prev,
      [indicatorKey]: !prev[indicatorKey],
    }));
  };

  const filteredIndicators = allIndicators.filter(i =>
    i.label.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <div style={{ marginBottom: '10px' }}>
        <button onClick={() => setTimeFrame(t => t + 100)}>🔼 Zaman Aralığını Genişlet</button>
        <button onClick={() => setTimeFrame(t => t - 100)}>🔽 Zaman Aralığını Küçült</button>
        <button onClick={() => {
          setContainerHeight(h => h + 100);
          setContainerHeightforIndicators(h => h + 50);
        }}>📏 Yüksekliği Artır</button>
        <button onClick={() => {
          setContainerHeight(h => h - 100);
          setContainerHeightforIndicators(h => h - 50);
        }}>📏 Yüksekliği Azalt</button>
        <button onClick={() => setModalVisible(true)}>🧮 İndikatör Seç</button>
      </div>

      {modalVisible && (
        <div style={{
          position: 'fixed',
          top: '10%',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: 'white',
          padding: '20px',
          boxShadow: '0 0 15px rgba(0,0,0,0.5)',
          zIndex: 1000
        }}>
          <h3>İndikatör Seç</h3>
          <input
            type="text"
            placeholder="İndikatör ara..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
          />
          <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
            {filteredIndicators.map(ind => (
              <div key={ind.key}>
                <label>
                  <input
                    type="checkbox"
                    checked={enabledIndicators[ind.key]}
                    onChange={() => handleCheckboxChange(ind.key)}
                  />
                  {ind.label}
                </label>
              </div>
            ))}
          </div>
          <hr />
          <div>
            <strong>Aktif İndikatörler:</strong>
            {Object.entries(enabledIndicators).filter(([k, v]) => v).map(([key]) => (
              <div key={key} style={{ marginBottom: '5px' }}>
              {key.toUpperCase()} <button onClick={() => handleCheckboxChange(key)}>❌</button>
            </div>
            ))}
          </div>
          <button onClick={() => setModalVisible(false)} style={{ marginTop: '10px' }}>Kapat</button>
        </div>
      )}

      <CandlestickChart chartData={chartData} containerHeight={containerHeight} bullTotalData={bullTotalData} bearishTotalData={bearishTotalData} nadarayaWatsonData={nadarayaWatsonData} />

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
