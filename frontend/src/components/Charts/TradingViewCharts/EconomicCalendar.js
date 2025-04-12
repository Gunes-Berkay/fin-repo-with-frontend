import { useEffect, useRef } from "react";

const TradingViewWidget = () => {
  const containerRef = useRef(null);

  useEffect(() => {
    const script = document.createElement("script");
    script.type = "text/javascript";
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-events.js";
    script.async = true;
    script.innerHTML = JSON.stringify({
      colorTheme: "dark",
      isTransparent: false,
      width: "400",
      height: "550",
      locale: "tr",
      importanceFilter: "0,1",
      countryFilter: "tr,us,eu,cn,jp",
    });

    if (containerRef.current) {
      containerRef.current.innerHTML = ""; // Önceki widget'ı temizle
      containerRef.current.appendChild(script);
    }
  }, []);

  return (
    <div className="tradingview-widget-container">
      <div ref={containerRef} className="tradingview-widget-container__widget"></div>
      <div className="tradingview-widget-copyright">
        <a
          href="https://tr.tradingview.com/"
          rel="noopener nofollow"
          target="_blank"
        >
          <span className="blue-text">Tüm piyasaları TradingView üzerinden takip edin</span>
        </a>
      </div>
    </div>
  );
};

export default TradingViewWidget;
