# 🚀 System Resource Monitoring Tool

A real-time system monitoring dashboard built using Python, designed to track CPU, memory, disk usage, and active processes with a smooth, non-blocking terminal interface.

---

## 📌 Overview

This project provides a lightweight alternative to traditional system monitors by displaying live system performance directly in the terminal. It uses efficient background processing to ensure a responsive and flicker-free experience.

---

## ⚙️ Features

* 📊 Real-time CPU, Memory, and Disk usage
* 🧠 Per-core CPU monitoring
* 🔥 Top processes based on CPU usage
* 🚨 Alerts for high resource consumption
* ⏱ System uptime tracking
* 🎨 Clean and dynamic terminal UI using Rich
* ⚡ Non-blocking design using multithreading

---

## 🧱 Tech Stack

* **Python**
* **psutil** → system-level data
* **rich** → terminal UI rendering
* **threading** → background processing

---

## 🧠 How It Works

* System metrics are fetched using `psutil`
* A background thread continuously updates process data
* The main thread renders a live dashboard using `Rich`
* Shared data is managed using thread-safe mechanisms (locks)
* The UI updates smoothly without blocking execution

---

## 📂 Project Structure

```bash
system_monitor.py   # Main application file
```

---

## ▶️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/system-monitor.git
cd system-monitor
```

### 2. Install dependencies

```bash
pip install psutil rich
```

### 3. Run the project

```bash
python system_monitor.py
```

---

## 🖥️ Demo

The application displays:

* System overview (CPU, Memory, Disk)
* Per-core usage
* Top running processes
* Alerts panel

*(Run locally to experience the live dashboard)*

---

## 🎯 Key Concepts Used

* Real-time monitoring
* Multithreading
* Non-blocking system design
* Caching & synchronization
* Terminal UI rendering

---

## ⚠️ Limitations

* Terminal-based (no GUI)
* Process stats may have slight refresh delay
* Some system-specific features may vary

---

## 🔮 Future Improvements

* GUI version (Tkinter / PyQt)
* Logging and analytics
* Network monitoring
* Historical performance graphs

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 👨‍💻 Author

Developed as part of a system-level Python project to demonstrate real-time monitoring and performance optimization techniques.

---

