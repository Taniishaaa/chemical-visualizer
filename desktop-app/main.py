import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QTextEdit
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


API_BASE = "http://127.0.0.1:8000/api"
AUTH = ("tanisha", "tanisha123")  


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Desktop Visualizer")
        self.setGeometry(200, 200, 700, 600)

        layout = QVBoxLayout()

        # Upload button
        self.upload_btn = QPushButton("Upload CSV")
        self.upload_btn.clicked.connect(self.upload_csv)
        layout.addWidget(self.upload_btn)

        # Summary display
        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        layout.addWidget(self.summary_box)

        # Matplotlib chart
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # History display
        self.history_label = QLabel("Last 5 Uploads:")
        layout.addWidget(self.history_label)

        self.history_box = QTextEdit()
        self.history_box.setReadOnly(True)
        layout.addWidget(self.history_box)

        # PDF download button
        self.pdf_btn = QPushButton("Download PDF Report")
        self.pdf_btn.clicked.connect(self.download_pdf)
        self.pdf_btn.setEnabled(False)
        layout.addWidget(self.pdf_btn)

        self.setLayout(layout)

        self.record_id = None
        self.load_history()

    # ---------------------------- API CALLS ----------------------------

    def load_history(self):
        try:
            res = requests.get(f"{API_BASE}/history/", auth=AUTH)
            records = res.json()

            text = ""
            for r in records:
                text += f"{r['filename']} — {r['total_count']} items\n"

            self.history_box.setText(text)
        except Exception as e:
            self.history_box.setText("Failed to load history.\n" + str(e))

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if not file_path:
            return

        try:
            with open(file_path, "rb") as f:
                res = requests.post(
                    f"{API_BASE}/upload-csv/",
                    files={"file": f},
                    auth=AUTH,
                )

            data = res.json()

            if "summary" not in data:
                self.summary_box.setText("Error: " + str(data))
                return

            summary = data["summary"]
            self.record_id = data["record_id"]
            self.pdf_btn.setEnabled(True)

            summary_text = (
                f"Total equipment: {summary['total_count']}\n"
                f"Average flowrate: {summary['avg_flowrate']:.2f}\n"
                f"Average pressure: {summary['avg_pressure']:.2f}\n"
                f"Average temperature: {summary['avg_temperature']:.2f}\n"
            )

            self.summary_box.setText(summary_text)

            # Draw chart
            self.draw_chart(summary["type_distribution"])

            # Reload history
            self.load_history()

        except Exception as e:
            self.summary_box.setText("Upload failed.\n" + str(e))

    def draw_chart(self, dist):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        labels = list(dist.keys())
        values = list(dist.values())

        ax.bar(labels, values)
        ax.set_title("Equipment Type Distribution")

        self.canvas.draw()

    def download_pdf(self):
        if not self.record_id:
            return

        try:
            res = requests.get(
                f"{API_BASE}/report/{self.record_id}/",
                auth=AUTH,
                stream=True
            )

            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save PDF Report",
                f"equipment_report_{self.record_id}.pdf",
                "PDF Files (*.pdf)"
            )

            if save_path:
                with open(save_path, "wb") as f:
                    f.write(res.content)

        except Exception as e:
            self.summary_box.setText("Failed to download PDF.\n" + str(e))


# ---------------------------- RUN APP ----------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
