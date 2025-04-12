const { app, BrowserWindow } = require("electron");
const { exec } = require("child_process");
const path = require("path");

let mainWindow;

// Backend ve Frontend klasörlerinin yolu
const backendPath = "C:\\Users\\kapov\\fin-demo\\fin-demo\\backend";
const frontendPath = "C:\\Users\\kapov\\fin-demo\\fin-demo\\backend";

// Django Backend'i Başlatan Fonksiyon
const { spawn } = require("child_process");

function startDjango() {
    return new Promise((resolve, reject) => {
        console.log("📢 Django backend başlatılıyor...");

        // PowerShell üzerinden Django sunucusunu çalıştır
        const djangoProcess = spawn('cmd.exe', ['/c', 'python', 'manage.py', 'runserver', '8000'],  { 
            cwd: backendPath,
            shell: true,
            env: process.env 
        });

        djangoProcess.stdout.on("data", (data) => {
            console.log(`Django: ${data}`);
            if (data.includes("Starting development server at http://")) {
                resolve();
            }
        });

        djangoProcess.stderr.on("data", (data) => {
            console.error(`Django Hata: ${data}`);
        });

        djangoProcess.on("error", (err) => reject(err));
    });
}

// React Frontend'i Başlatan Fonksiyon
function startReact() {
    return new Promise((resolve, reject) => {
        console.log("🚀 React frontend başlatılıyor...");
        const reactProcess =  spawn("npm", ["start"],{ 
            cwd: frontendPath,
            shell: true,
            env: process.env 
        });

        reactProcess.stdout.on("data", (data) => {
            console.log(`React: ${data}`);
            if (data.includes("Compiled successfully") || data.includes("You can now view")) {
                resolve(); // React başlatıldı
            }
        });

        reactProcess.stderr.on("data", (data) => {
            console.error(`React Hata: ${data}`);
        });

        reactProcess.on("error", (err) => reject(err));
    });
}

// Electron Uygulamasını Başlat
app.whenReady().then(async () => {
    try {
        await startDjango(); // Django'yu başlat ve tamamlanmasını bekle
        await startReact();  

        mainWindow = new BrowserWindow({
            width: 1200,
            height: 800,
            webPreferences: {
                nodeIntegration: true,
            },
        });

        // React uygulamasını yükle
        mainWindow.loadURL("http://localhost:3000");

        mainWindow.on("closed", () => {
            mainWindow = null;
        });

    } catch (error) {
        console.error("Uygulama başlatılırken hata oluştu:", error);
    }
});

// Tüm pencereler kapanınca uygulamayı kapat
app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
        app.quit();
    }
});
