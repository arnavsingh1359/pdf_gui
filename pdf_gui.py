import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, \
    QListWidget, QHBoxLayout, QListWidgetItem, QMessageBox
import PyPDF2


class PdfEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.file_path = ""
        self.page_order = []

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Select a PDF file:")
        layout.addWidget(self.label)

        self.button_browse = QPushButton("Browse", self)
        self.button_browse.clicked.connect(self.browse_pdf)
        layout.addWidget(self.button_browse)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()

        self.button_merge = QPushButton("Merge PDFs", self)
        self.button_merge.clicked.connect(self.merge_pdfs)
        button_layout.addWidget(self.button_merge)

        self.button_split = QPushButton("Split PDF", self)
        self.button_split.clicked.connect(self.split_pdf)
        button_layout.addWidget(self.button_split)

        self.button_rearrange = QPushButton("Re-arrange Pages", self)
        self.button_rearrange.clicked.connect(self.rearrange_pages)
        button_layout.addWidget(self.button_rearrange)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.setWindowTitle("PDF Editor")
        self.resize(1000, 700)
        self.show()

    def browse_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            self.file_path = file_path
            self.label.setText(f"Selected PDF file: {self.file_path}")
            self.load_page_list()

    def load_page_list(self):
        self.list_widget.clear()
        self.page_order = []

        if self.file_path:
            with open(self.file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                for page_num in range(1, num_pages, 1):
                    item = QListWidgetItem(f"Page {str(page_num).zfill(len(str(num_pages)))} / {num_pages}")
                    self.list_widget.addItem(item)
                    self.page_order.append(page_num)

    def merge_pdfs(self):
        input_files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files to Merge", "", "PDF Files (*.pdf)")
        output_file, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")

        if input_files and output_file:
            pdf_merger = PyPDF2.PdfMerger()

            for file in input_files:
                pdf_merger.append(file)

            with open(output_file, "wb") as output:
                pdf_merger.write(output)

            QMessageBox.information(self, "Success", "PDFs merged successfully!")

    def split_pdf(self):
        if not self.file_path:
            QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")

        if output_dir:
            with open(self.file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                num_pages = len(pdf_reader.pages)

                for page_num in range(1, num_pages+1):
                    pdf_writer = PyPDF2.PdfWriter()
                    pdf_writer.add_page(pdf_reader.pages[page_num-1])

                    output_file = f"{output_dir}/page_{str(page_num).zfill(len(str(num_pages)))}.pdf"
                    with open(output_file, "wb") as output:
                        pdf_writer.write(output)

            QMessageBox.information(self, "Success", "PDF split successfully!")

    def rearrange_pages(self):
        if not self.file_path:
            QMessageBox.warning(self, "Warning", "Please select a PDF file first.")
            return

        num_pages = self.list_widget.count()

        if num_pages == 0:
            QMessageBox.warning(self, "Warning", "No pages to rearrange.")
            return

        # Create a temporary PDF file to store the rearranged pages
        temp_file_path = "temp_rearranged.pdf"

        with open(self.file_path, "rb") as input_file:
            pdf_reader = PyPDF2.PdfFileReader(input_file)
            pdf_writer = PyPDF2.PdfWriter()

            # Rearrange pages based on the user's order
            for index in range(num_pages):
                page_num = self.page_order[index]
                pdf_writer.addPage(pdf_reader.pages[page_num])

            # Write the rearranged pages to the temporary file
            with open(temp_file_path, "wb") as temp_file:
                pdf_writer.write(temp_file)

        # Replace the original file with the rearranged file
        import os
        os.remove(self.file_path)
        os.rename(temp_file_path, self.file_path)

        # Reload the page list
        self.load_page_list()

        QMessageBox.information(self, "Success", "Pages rearranged successfully!")


if __name__ == "__main__":

    print("Running PDF Editor...")
    print("You can merge PDFs by clicking on the 'Merge PDFs' button.")
    print("You can split PDFs by clicking on the 'Split PDF' button.")
    print("You can rearrange pages by clicking on the 'Rearrange Pages' button.")

    app = QApplication(sys.argv)
    editor = PdfEditor()
    sys.exit(app.exec_())
