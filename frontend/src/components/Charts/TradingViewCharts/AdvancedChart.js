// TradingViewWidget.jsx
import React, { useEffect, useRef, memo } from 'react';

function TradingViewWidget( { symbol, watchlist, indicators } ) {
  const container = useRef(null);


  useEffect(
    () => {
      const script = document.createElement("script");
      script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
      script.type = "text/javascript";
      script.async = true;
      script.textContent =JSON.stringify({
        symbol: "BINANCE:"+symbol ,
        interval: "240",
        timezone: "Europe/Istanbul",
        theme: "dark",
        style: "1",
        locale: "tr",
        withdateranges: true,
        hide_side_toolbar: false,
        allow_symbol_change: true,
        watchlist: watchlist,
        studies : indicators,
        details: true,
        hotlist: true,
        calendar: false,
        show_popup_button: true,
        popup_width: "1700",
        popup_height: "800",
        support_host: "https://www.tradingview.com"
      });
      if (container.current) {
        container.current.innerHTML = "";
        container.current.appendChild(script);
      }
      
    },
    [symbol, watchlist, indicators]
  );

  return (
    <div className="tradingview-widget-container" ref={container} style={{ height: "600px" , width:"80%" }}>
      {/* Bu div'e height: "600px" gibi bir değer ekleyerek boyutu kontrol edebilirsiniz */}
      <div className="tradingview-widget-container__widget" style={{ height: "600px", width: "100%" }}></div>
      <div className="tradingview-widget-copyright">
        <a href="https://tr.tradingview.com/" rel="noopener nofollow" target="_blank">
          <span className="blue-text">Tüm piyasaları TradingView üzerinden takip edin</span>
        </a>
      </div>
    </div>
  );
}

export default memo(TradingViewWidget);
