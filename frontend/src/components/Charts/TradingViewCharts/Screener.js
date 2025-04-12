import React, { useEffect, useRef } from "react";

const TradingViewScreener = () => {
  const containerRef = useRef(null);

  useEffect(() => {
    const script = document.createElement("script");
    script.src =
      "https://s3.tradingview.com/external-embedding/embed-widget-screener.js";
    script.type = "text/javascript";
    script.async = true;
    script.innerHTML = JSON.stringify({
      width: "100%",
      height: 550,
      defaultColumn: "overview",
      defaultScreen: "below_52wk_low",
      market: "turkey",
      showToolbar: true,
      colorTheme: "dark",
      locale: "tr",
    });

    containerRef.current.innerHTML = "";
    containerRef.current.appendChild(script);
  }, []);

  return (
    <div
      className="tradingview-widget-container"
      ref={containerRef}
      style={{ width: "100%", height: "550px" }}
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

export default TradingViewScreener;
