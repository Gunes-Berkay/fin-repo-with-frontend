import React, { useEffect, useRef } from "react";

const TradingViewForexHeatMap = () => {
  const containerRef = useRef(null);

  useEffect(() => {
    const script = document.createElement("script");
    script.src =
      "https://s3.tradingview.com/external-embedding/embed-widget-forex-heat-map.js";
    script.type = "text/javascript";
    script.async = true;
    script.innerHTML = JSON.stringify({
      width: 550,
      height: 400,
      currencies: ["EUR", "USD", "JPY", "CNY", "TRY"],
      isTransparent: false,
      colorTheme: "dark",
      locale: "tr",
      backgroundColor: "#1D222D",
    });

    containerRef.current.innerHTML = "";
    containerRef.current.appendChild(script);
  }, []);

  return (
    <div
      className="tradingview-widget-container"
      ref={containerRef}
      style={{ width: "550px", height: "400px" }}
    >
      <div
        className="tradingview-widget-container__widget"
        style={{ height: "100%" }}
      ></div>
      <div className="tradingview-widget-copyright">
        <a
          href="https://tr.tradingview.com/"
          rel="noopener nofollow"
          target="_blank"
        >
          <span className="blue-text">
            Tüm piyasaları TradingView üzerinden takip edin
          </span>
        </a>
      </div>
    </div>
  );
};

export default TradingViewForexHeatMap;
