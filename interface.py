from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget,
    QFileDialog, QMessageBox, QProgressBar, QComboBox, QLineEdit, QHBoxLayout
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import os
import fitz
import matplotlib.pyplot as plt
from io import BytesIO
from Ai import WorkerThread
from fpdf import FPDF


class CompatibilidadeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔍 Analisador de Currículos Inteligente")
        self.setGeometry(300, 200, 1000, 700)
        self.setMinimumSize(800, 600)
        self.file_history = []
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()

        self.status_label = QLabel("Pronto para analisar")
        self.status_label.setFont(QFont("Segoe UI", 10))

        demands_layout = QHBoxLayout()
        self.demands_label = QLabel("Habilidades Exigidas (separadas por vírgula):")
        self.demands_input = QLineEdit("SQL,PYTHON,GIT,FASTAPI,NODE.JS")
        demands_layout.addWidget(self.demands_label)
        demands_layout.addWidget(self.demands_input)

        self.history_combo = QComboBox()
        self.history_combo.addItem("Selecione um currículo recente")
        self.history_combo.currentIndexChanged.connect(self.load_from_history)

        self.resultado_label = QLabel("Resultados da Análise:")
        self.resultado_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        self.texto_extraido = QTextEdit()
        self.texto_extraido.setReadOnly(True)

        button_layout = QHBoxLayout()
        self.botao_carregar = QPushButton("📂 Selecionar Currículo PDF")
        self.botao_carregar.clicked.connect(self.abrir_pdf)
        self.botao_exportar = QPushButton("📄 Exportar Relatório")
        self.botao_exportar.clicked.connect(self.exportar_relatorio)
        self.botao_clear = QPushButton("🗑 Limpar")
        self.botao_clear.clicked.connect(self.clear_ui)
        button_layout.addWidget(self.botao_carregar)
        button_layout.addWidget(self.botao_exportar)
        button_layout.addWidget(self.botao_clear)

        self.saida_resultado = QTextEdit()
        self.saida_resultado.setReadOnly(True)

        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)

        layout.addWidget(self.status_label)
        layout.addLayout(demands_layout)
        layout.addWidget(self.history_combo)
        layout.addWidget(self.resultado_label)
        layout.addWidget(self.texto_extraido)
        layout.addLayout(button_layout)
        layout.addWidget(self.saida_resultado)
        layout.addWidget(self.chart_label)
        layout.addWidget(self.progress_bar)

        central.setLayout(layout)

    def apply_styles(self):
        background = "#1e1e2f"
        text_color = "#f0f0f0"
        accent_color = "#4e9af1"
        border_color = "#3a3f58"
        button_hover = "#3b6db3"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {background};
                color: {text_color};
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }}
            QLabel {{
                color: {accent_color};
                font-size: 15px;
                padding: 4px 0;
            }}
            QTextEdit, QLineEdit, QComboBox {{
                background-color: #2b2e3b;
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 6px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            QProgressBar {{
                background-color: #2b2e3b;
                border: 1px solid {border_color};
                border-radius: 5px;
                text-align: center;
                color: {text_color};
            }}
            QProgressBar::chunk {{
                background-color: {accent_color};
            }}
        """)

    def abrir_pdf(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, "Abrir Currículo PDF", "", "Arquivos PDF (*.pdf)")
        if arquivo:
            self.status_label.setText("Carregando PDF...")
            try:
                with fitz.open(arquivo) as doc:
                    texto = "".join([page.get_text() for page in doc])
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao ler o PDF: {e}")
                self.status_label.setText("Erro ao carregar")
                return

            self.texto_extraido.setText(texto)
            if arquivo not in self.file_history:
                self.file_history.append(arquivo)
                self.history_combo.addItem(os.path.basename(arquivo))
            self.analisar_curriculo(texto)
            self.status_label.setText("Análise concluída")

    def load_from_history(self):
        index = self.history_combo.currentIndex()
        if index > 0:
            arquivo = self.file_history[index - 1]
            try:
                with fitz.open(arquivo) as doc:
                    texto = "".join([page.get_text() for page in doc])
                self.texto_extraido.setText(texto)
                self.analisar_curriculo(texto)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar do histórico: {e}")

    def analisar_curriculo(self, texto):
        demands_text = self.demands_input.text().strip()
        if not demands_text:
            QMessageBox.warning(self, "Aviso", "Por favor, insira as habilidades exigidas!")
            return
        empresa_demands = {d.strip().upper() for d in demands_text.split(",")}

        self.progress_bar.setValue(0)
        self.status_label.setText("Analisando currículo...")
        self.worker_thread = WorkerThread(texto, empresa_demands)
        self.worker_thread.update_progress.connect(self.update_progress)
        self.worker_thread.finished.connect(self.show_result)
        self.worker_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def show_result(self, resultado, compatividade, missing_skills):
        self.saida_resultado.setText(resultado)
        self.progress_bar.setValue(100)
        self.status_label.setText("Análise concluída")
        self.display_chart(compatividade, missing_skills)

    def display_chart(self, compatividade, missing_skills):
        compatividade = max(0, min(compatividade, 100))
        restante = max(0, 100 - compatividade)

        plt.figure(figsize=(4, 4))
        labels = ['Compatível', 'Não Compatível']
        sizes = [compatividade, restante]
        colors = ['#4e9af1', '#ff4d4d']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')

        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close()
        buffer.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        self.chart_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        buffer.seek(0)
        self.chart_buffer = buffer

    def exportar_relatorio(self):
        relatorio = self.saida_resultado.toPlainText()
        if not relatorio.strip():
            QMessageBox.warning(self, "Aviso", "Não há dados para exportar!")
            return

        try:
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads_path, exist_ok=True)
            export_path = os.path.join(downloads_path, "relatorio_analise.pdf")

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            relatorio_encoded = relatorio.encode('latin-1', errors='replace').decode('latin-1')
            pdf.multi_cell(0, 10, relatorio_encoded)

            if hasattr(self, 'chart_buffer'):
                chart_path = os.path.join(downloads_path, "temp_chart.png")
                with open(chart_path, 'wb') as img_file:
                    img_file.write(self.chart_buffer.getvalue())
                pdf.image(chart_path, x=10, y=pdf.get_y() + 10, w=90)

            pdf.output(export_path)
            QMessageBox.information(self, "Sucesso", f"Relatório salvo automaticamente em:\n{export_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar o relatório: {e}")

    def clear_ui(self):
        self.texto_extraido.clear()
        self.saida_resultado.clear()
        self.progress_bar.setValue(0)
        self.chart_label.clear()
        self.status_label.setText("Pronto para analisar")
        self.history_combo.setCurrentIndex(0)
